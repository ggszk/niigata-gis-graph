#
# kmlファイルに含まれる道の数を数える
#

import datetime
import json

#
# 道ファイルを作成する 
# 1行が道を表す：座標の並び（coordinatesタグの中身そのまま）
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
def get_intersections(file) :
    # 道路ファイルを読む
    roads = read_roads(file)

    print(datetime.datetime.now())

    # 交点を求める
    limit = 100 # 道の数：デバッグ用
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
        print(json.dumps(intersections))
        i = i + 1

    print(datetime.datetime.now())

# ここからデータの作成

# 入力となるKMLファイル
kml_files = ["./data/od_gis_10121_kokudo.kml", "./data/od_gis_10122_kendo.kml", "./data/od_gis_10123_shido.kml"]

# 中間生成ファイルの置き場
temp_dir = "./result_temp/"

# 道データの作成
create_roads_file(kml_files, temp_dir + "roads.txt")

# 重複する点の排除：一つの道で同じ座標が2つ連続して出てくるとき、その重複を削除する
remove_duplicate_points(temp_dir + "roads.txt", temp_dir + "roads2.txt")

# 道路ファイルから交点ファイルを作る
get_intersections(temp_dir + "roads2.txt")