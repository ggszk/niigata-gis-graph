#
# kmlファイルに含まれる道の数を数える
#

import datetime
import json

def count_road(file) :
    r_cnt = 0
    with open(file) as f:
        for line in f:
            # 文字列LineStringが含まれていたら道と判断
            if "LineString" in line :
                r_cnt = r_cnt + 1
    return r_cnt

file1 = "./data/od_gis_10121_kokudo.kml"
file2 = "./data/od_gis_10122_kendo.kml"
file3 = "./data/od_gis_10123_shido.kml"

#print(count_road(file1))
#print(count_road(file2))
#print(count_road(file3))

#
# 線分ファイルを作成する 
# 行が線分

def print_segments(file) :
    with open(file) as f:
        for line in f:
            if "LineString" in line :
                # coordinatesタグの中身を取る
                segment_str = line.split("<coordinates>")[1].split("</coordinates>")[0]
                print(segment_str)

#print_segments("./data/od_gis_10121_kokudo.kml")
#print_segments("./data/od_gis_10122_kendo.kml")
#print_segments("./data/od_gis_10123_shido.kml")

# 重複する点の排除：同じ座標が2つ続くパターンを消す
def remove_duplicate_points(file) :
    with open(file) as f:
        for line in f:
            coordinates = line.split()
            prev_point = ""
            for c in coordinates :
                if prev_point != c :
                    print(c + " ", end='')
                prev_point = c
            print("")

#remove_duplicate_points("roads.txt")

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

#segments = read_roads("roads.txt")
#print(segments)

#
# 区間の交わりを判定
# 区間：数値2つのタプル．大小の制約はなし（(大, 小）でもよい）
# 返り値：0→交わる，1→i1が右側，-1→i2が右側
#
def is_disjoint_i(i1, i2) :
    # normalize: もし端点の大小が逆なら入れ替える
    if i1[0] > i1[1] :
        i1 = (i1[1], i1[0])
    if i2[0] > i2[1] :
        i1 = (i2[1], i2[0])
    if i1[1] > i2[1] :
        if i2[1] < i1[0] :
            return 1
        else :
            return 0
    if i2[1] > i1[1] :
        if i1[1] < i2[0] :
            return -1
        else :
            return 0

#
# 道が交わるかを確認：おおまかに交わらないものを除外
# s1, s2：線分→座標の配列　例）[(139.04299140672896, 37.87088205211192), (139.04296467845813, 37.87097263872479)]
# 返り値：0 交わる(かもしれない) 1 交わらない
def check_cross_segments(s1, s2):
    # y軸方向で十分離れている
    y_i1 = (s1[0][1], s1[1][1])
    y_i2 = (s2[0][1], s2[1][1])
    result_y = is_disjoint_i(y_i1, y_i2)
    # x軸方向で十分離れている
    x_i1 = (s1[0][0], s1[1][0])
    x_i2 = (s2[0][0], s2[1][0])
    # どちらかの軸方向で離れていれば，必ず交わらない
    result_x = is_disjoint_i(x_i1, x_i2)
    if result_y != 0 or result_x != 0 :
        return 1
    else :
        return 0

#print(check_cross_segments([(0,2),(1,3)],[(2,4),(5,0)]))
#print(check_cross_segments([(0,2),(1,3)],[(0,4),(5,0)]))

#print(is_disjoint_i((1,2),(3,4)))
#print(is_disjoint_i((3,4),(1,2)))
#print(is_disjoint_i((3,4),(1,3)))
#print(is_disjoint_i((4,3),(1,3)))
#print(is_disjoint_i((3,4),(3,1)))
#print(is_disjoint_i((3,4),(1,5)))

# 県道
r1 = [
    (139.06137121229557,37.908416201176138),
    (139.06283170142572,37.908828832460294),
    (139.06338868109475,37.908958708084398),
    (139.06391867440607,37.909113668696826),
    (139.06426602258466,37.909222919828714),
    (139.06473468440777,37.909357987863565),
    (139.06500975497411,37.909443796574891),
    (139.06665831454328,37.909906655247042)
]
# 市道
r2 = [
    (139.06256880511037,37.910117200348552),
    (139.06314199086879,37.908791217211906),
    (139.06373716476827,37.907294291772146),
    (139.06563998077024,37.902606598905408),
    (139.0669936776001,37.899234941726519),
    (139.06780359976915,37.897175260573896)
]

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

#l1 = get_line(r1[0], r1[1])
#l2 = get_line(r2[0], r2[1])
#print(l1)
#print(l2)
#print(get_intersection(l1, l2))

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

#s0 = (r1[1], r1[2])
#s1 = (r2[0], r2[1])
#print(get_intersection_of_segments(s0, s1))

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
    
#print(get_intersection_of_roads(r1, r2))

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

# 0 divideの調査．同じ座標はあるのか？
def same_coordinates() :
    roads = read_roads("roads.txt")

    # 交点を求める
    limit = 1000 # 道の数：デバッグ用
    i = 0
    for r0 in roads:
        j = 0
        for r1 in roads:
            if i != j :
                for p0 in r0 :
                    for p1 in r1 :
                        # x座標が同じだったら出力
                        if p0[0] == p1[0] :
                            print(str(i)+","+str(j) , end='')
                            print(p0, end='')
                            print(p1)
            j = j + 1
            if j == limit :
                break
        i = i + 1
        if i == limit :
            break

# 隣どおしに同じ座標がないか調べる
def same_coordinates2() :
    roads = read_roads("roads2.txt")

    # 交点を求める
    limit = 20000 # 道の数：デバッグ用
    i = 0
    for r0 in roads:
        j = 0
        for p0 in r0 :
            if j == len(r0) - 1:
                break
            p1= r0[j+1]
#            print(p0, end='')
#            print(p1, end='')
            # x座標が同じだったら出力
            if p0[0] == p1[0] :
                print(str(i)+","+str(j), end='')
                print(p0, end='')
                print(p1)
            j = j + 1
            if j == limit :
                break
 #       print("")
        if i == limit :
            break
        i = i + 1

#same_coordinates2()

#get_intersections("roads2.txt")