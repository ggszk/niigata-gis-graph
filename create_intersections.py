#
# 交点ファイルの作成
#

import datetime
import json

#
# 道路ファイルを作成する 
# 1行が道を表す：座標の並び（coordinatesタグの中身そのまま）
# in_files : KML形式のファイル名のリスト
# out_file : 道路ファイル
#
def create_roads_file(in_files, out_file) :
    with open(out_file, "w") as o_f:
        for in_file in in_files:
            with open(in_file) as f:
                for line in f:
                    if "LineString" in line :
                        # coordinatesタグの中身を取る
                        segment_str = line.split("<coordinates>")[1].split("</coordinates>")[0]
                        o_f.write(segment_str + "\n")

#
# 重複する点の排除
# 重複は必ず連続して発生することを仮定（ソートされている）
# 入力：road →道路＝座標の配列
# 出力：out_road→重複が排除された道路
def remove_duplicate_points_road(road) :
    out_road = []
    prev_point = ""
    for c in road :
        if prev_point != c :
            out_road.append(c)
        prev_point = c
    return out_road

#
# 重複する点の排除：一つの道で同じ座標が2つ連続して出てくるとき、その重複を削除する
# 重複が残ると、2点を通る直線を求めるときに0 divideエラーとなる
#
def remove_duplicate_points(file, out_file) :
    with open(out_file, "w") as o_f:
        with open(file) as f:
            for line in f:
                coordinates = line.split()
                prev_point = ""
                for c in coordinates :
                    if prev_point != c :
                        o_f.write(c + " ")
                    prev_point = c
                o_f.write("\n")

#
# 道ファイルを読む（点の集まりが道）
#
def read_roads(file) :
    roads = []
    with open(file) as f:
        for line in f:
            road = []
            coordinates = line.split()
            for c in coordinates :
                t = tuple(c.split(','))
                t_f = (float(t[0]), float(t[1]))
                road.append(t_f)
            roads.append(road)
    return roads

# 2点を通る直線の傾きと切片の組を返す
def get_line(p0, p1) :
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]

    return ((y1-y0)/(x1-x0), (y0*x1-x0*y1)/(x1-x0))

# 2つの直線の交点を返す．直線とは傾きと切片の組
# 直線が平行ならNoneを返す
def get_intersection(l0, l1) :
    ret = None
    a0 = l0[0]
    b0 = l0[1]
    a1 = l1[0]
    b1 = l1[1]
    if a0 != a1 :
        ret = ((b1-b0)/(a0-a1), (a0*b1-b0*a1)/(a0-a1))
    return ret

# 2つの線分の交点を返す．線分は2点の組．交点がない場合はNoneを返す
def get_intersection_of_segments(s0, s1) :
    # s0とs1に含まれる2点を，x座標の順に並べ直す
    if s0[0][0] > s0[1][0] :
        s0 = (s0[1], s0[0])
    if s1[0][0] > s1[1][0] :
        s1 = (s1[1], s1[0])
    # 線分の直線を求める
    l0 = get_line(s0[0], s0[1])
    l1 = get_line(s1[0], s1[1])
    # 直線の交点を求める
    p = get_intersection(l0, l1)
    # 交点が線分上にあれば，それを返す．x座標が両方の線分の範囲内にあれば大丈夫
    ret = None
    if p is not None and (p[0] >= s0[0][0] and p[0] <= s0[1][0]) and (p[0] >= s1[0][0] and p[0] <= s1[1][0]) :
        ret = p
    return ret

# 道（線分の集まり）の交点（のリスト）を求める
# 結果は，交点のあった線分のインデックスの組と交点の座標　の組
def get_intersection_of_roads(r0, r1) :
    # 交点は複数あるかもしれないからリスト
    ret = []
    i = 0
    for p0 in r0:
        if i == len(r0) - 1 :
            break
        s0 = (r0[i], r0[i+1])
        j = 0
        for p1 in r1:
            if j == len(r1) - 1:
                break
            s1 = (r1[j], r1[j+1])
            p = get_intersection_of_segments(s0, s1)
            if p is not None :
                ret.append([i, j, list(p)])
            j = j + 1
        i = i + 1
    return ret

# 道路ファイルから交点ファイルを作る
# JSONに出力する都合でタプルをリストにしている
def get_intersections(file, out_file) :
    # 道路ファイルを読む
    roads = read_roads(file)

    # 交点を求める
    limit = 100 # 道の数：デバッグ用
    with open(out_file, "w") as o_f:
        i = 0
        for r0 in roads:
            if i == limit :
                break
            j = 0
            intersections = []
            for r1 in roads:
                if j == limit :
                    break
                # 同じ道の間の交点は求めない→交点はr0とr1入れ替えて2回計算されている
                if i != j :
                    p = get_intersection_of_roads(r0, r1)
                    # 交点があったら出力
                    if len(p) > 0 :
                        intersections.append([j, p])
                j = j + 1
            o_f.write(json.dumps(intersections) + "\n")
            i = i + 1

# 緯度・経路の範囲を求める
# file 道路ファイル名
# n 縦（横）を分割する個数→n*nのメッシュができる
# 出力：緯度の最小最大の組み，経度の最小最大の組み，緯度経度のセルサイズの組み，n（入力そのまま）
def get_region(file, n) :
    min_x = 200
    max_x = 0
    min_y = 200
    max_y = 0
    w = 0   # セルの横幅
    h = 0   # セルの縦幅

    roads = read_roads(file)
    for r in roads:
        for p in r:
            if p[0] < min_x :
                min_x = p[0]
            if p[0] > max_x :
                max_x = p[0]
            if p[1] < min_y :
                min_y = p[1]
            if p[1] > max_y :
                max_y = p[1]
    w = (max_x - min_x)/n
    h = (max_y - min_y)/n

    return [(min_x, max_x), (min_y, max_y), (w, h), n]

# 点の含まれるセルを求める
# 入力：p→点，regiron→get_regionの出力
# 出力：セルのインデックス（整数の組み）
def get_cell_by_point(p, region) :
    # 原点の座標は，(min_x, min_y)
    origin = (region[0][0], region[1][0])
    
    w = region[2][0]
    h = region[2][1]
    n = region[3]

    result_x = int((p[0] - origin[0])//w)
    result_y = int((p[1]-origin[1])//h)
    # 座標が最大値に一致する場合は，セルを-1する必要あり（indexがnに等しくなってしまう）
    if result_x == n :
        result_x = n - 1 
    if result_y == n :
        result_y = n - 1 
    return (result_x, result_y)

# 線分と交わる領域を求める
# 簡易的に線分が含まれる長方形とする
# 入力：s→線分，regiron→get_regionの出力
# 出力：左端と右端のセルの組み
def get_cells_by_segment(s, region) :
    # sの端点を，x座標の順に並べ直す
    if s[0][0] > s[1][0] :
        s = (s[1], s[0])

    # 端点が含まれるセルを求める
    cell0 = get_cell_by_point(s[0], region)
    cell1 = get_cell_by_point(s[1], region)

    return (cell0, cell1)

# 簡易空間インデックスの作成
# file 道路ファイル名
# out_file 作成されるインデックスファイル名
# region 点の存在する範囲（get_regionの出力）
# 出力：インデックスファイル→セルインデックス，（線分とその線分を含む道路のIDの組み）のリスト
def create_index(file, out_file, region) :
    # 道路ファイルを読む
    roads = read_roads(file)

    # 縦（横）を分割する個数
    n = region[3]

    # インデックスを空のリストで初期化
    index = []
    for i in range(n) :
        row = []
        for j in range(n):
            row.append([])
        index.append(row)

    r_no = 0 # 道路の番号
    for r in roads:
        i = 0 # 点の番号
        for p in r:
            if i == len(r) - 1 :
                break
            s = (r[i], r[i+1])
            # 線分の端点のセルを求める
            cells = get_cells_by_segment(s, region)
            # 端点を含む長方形に含まれるセルをインデックスに追加する
            min_x = min(cells[0][0], cells[1][0])
            max_x = max(cells[0][0], cells[1][0])
            min_y = min(cells[0][1], cells[1][1])
            max_y = max(cells[0][1], cells[1][1])

            for cell_x in range(min_x, max_x+1) :
                for cell_y in range(min_y, max_y+1) :
                    index[cell_x][cell_y].append((s, r_no))
            i = i + 1
        r_no = r_no + 1
    return index

# インデックスの構造を線分の集まりから，道路の集まりに変換
# →将来的にはcreate_indexで一気にやったほうがいいかも
def create_index2(index) :
    index2 = []
    r_no = -1 # 道路番号
    p_list = [] # 道路上の点座標リスト

    for col in index :
        col2 = []
        # 列？行？
        for cell in col :
            cell2 = []
            # 道路がなければ空リストを入れる
            if len(cell) == 0 :
                col2.append([])
                continue
            # 線分
            s_i = 0
            for s in cell :
                # 新しい道路に移る（最初の1回はやらない）か，cellの中の最後の線分になったらcell2にリストを加える
                if (s[1] != r_no and r_no != -1) or s_i == len(cell)-1 :
                    p_list.append(s[0][1]) # 最後の1つの点
                    # p_listの重複排除→どこで重複発生しているか要調査
                    p_list = remove_duplicate_points_road(p_list)
                    cell2.append((r_no, p_list))
                    r = []
                    p_list = []
                r_no = s[1]
                p_list.append(s[0][0]) # 次のs[1]と前のs[0]は必ず等しい（そう作った）
                s_i = s_i + 1
            col2.append(cell2)            
        index2.append(col2)

    return index2

# 簡易空間インデックスにおけるインデックスから領域の緯度経度を返す
def get_coordinate(i, j, region) :
    origin = (region[0][0], region[1][0])

    w = region[2][0]
    h = region[2][1]

    min_x = origin[0] + w*i
    max_x = min_x + w
    min_y = origin[1] + h*j
    max_y = min_y + h

    return [(min_x, max_x), (min_y, max_y)]

# 簡易空間インデックスから交点ファイルを作る
# JSONに出力する都合でタプルをリストにしている
def get_intersections_from_index(index, region, roads, road_num, out_file) :
    cell_i = 0
    intersections_list = []
    for col in index :
        cell_j = 0
        for cell in col :
            # セルの範囲求める
            cell_coord = get_coordinate(cell_i, cell_j, region)
            # 道路が2つ以上ある場合のみ，道路の組み合わせで交点を求める
            cell_j = cell_j + 1
            if len(cell) < 2 :
                continue
            # 各セルで交点を求める
            intersections = []
            for r0 in cell:
                for r1 in cell:
                    # 同じ道の間の交点は求めない→交点はr0とr1入れ替えて2回計算されている
                    if r0[0] != r1[0] :
                        p = get_intersection_of_roads(r0[1], r1[1])
                        # 交点があったら出力
                        if len(p) > 0 :
                            # 線分のID（これは道路の中の点のID）をセル中のIDではなく，道路全体の中でのIDに書き換える
                            result_p = []
                            for p2 in p :
                                # セル中のIDから座標を求める
                                c0 = r0[1][p2[0]]
                                c1 = r1[1][p2[1]]
                                # その座標の道路全体の中でのIDを求める
                                pos0 = get_pos_in_road(c0, r0[0], roads)
                                pos1 = get_pos_in_road(c1, r1[0], roads)
                                # IDの書き換え
                                p2[0] = pos0
                                p2[1] = pos1
                                # 交点がセルの中になかったら除外（本当は早めに除外するほうがよいが）
                                if in_cell(p2[2], cell_coord) :
                                    result_p.append(p2)
                            if len(result_p) > 0:
                                intersections.append([(r0[0],r1[0]), result_p])
            intersections_list.append(intersections)
            #print(json.dumps(intersections))
        cell_i = cell_i + 1

    # 交点ファイルのデータ構造．1行が道路を表す
    road_list = []
    for r in range(road_num) :
        road_list.append([])

    # 交点ファイルの形式に変換する
    for intersections in intersections_list :
        for intersection in intersections :
            r0_no = intersection[0][0]
            r1_no = intersection[0][1]
            c = intersection[1]
            road_list[r0_no].append([r1_no, c])

    # 交点ファイルの出力
    with open(out_file, "w") as o_f:
        for rr in road_list :
            o_f.write(json.dumps(rr) + "\n")
    return

# 点がセルに入るかどうかを判定
def in_cell(p, cell):
    result = False

    min_x = cell[0][0]
    max_x = cell[0][1]
    min_y = cell[1][0]
    max_y = cell[1][1]

    x = p[0]
    y = p[1]

    if min_x <= x and x <= max_x and min_y <=y and y <= max_y :
        result = True

    return result

# 座標と道路の番号を入れて，道路リストから，座標がその道路中の何番目にあるかを求める
def get_pos_in_road(c, r_no, roads) :
    result = None
    i = 0
    for r_c in roads[r_no] :
        if c == r_c :
            result = i
        i = i + 1
    return result

# インデックスをファイル出力
def print_index(index) :
    # 1行あたりの線分数の最大を調べる
    max_seg = 0
    col_i = 0
    for col in index :
        row_i = 0
        for cell in col :
            if len(cell) > max_seg :
                max_seg = len(cell)
#            print(len(cell))
#            print(str(col_i) + " " + str(row_i), end='') # for debug
            print(cell)
            row_i = row_i + 1
        col_i = col_i + 1
#    print(max_seg)

# ここからデータの作成

# 入力となるKMLファイル
kml_files = ["./input/od_gis_10121_kokudo.kml", "./input/od_gis_10122_kendo.kml", "./input/od_gis_10123_shido.kml"]

# 中間生成ファイルの置き場
temp_dir = "./temp/"

# 道路ファイルの作成
create_roads_file(kml_files, temp_dir + "roads.txt")

# 重複する点の排除：一つの道で同じ座標が2つ連続して出てくるとき、その重複を削除する
remove_duplicate_points(temp_dir + "roads.txt", temp_dir + "roads2.txt")

# 道路ファイルから交点ファイルを作る
print(datetime.datetime.now())
# ↓これはインデックスを使わない場合
# get_intersections(temp_dir + "roads2.txt", temp_dir + "intersections.txt")

# ↓これはインデックスを使う場合
region = get_region(temp_dir + "roads2.txt", 200)
index = create_index(temp_dir + "roads2.txt", "", region)
index2 = create_index2(index)
roads = read_roads(temp_dir + "roads2.txt")
get_intersections_from_index(index2, region, roads, len(roads), temp_dir + "intersections.txt")
print(datetime.datetime.now())
