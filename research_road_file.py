#
# 道路ファイル中のデータに関する事前調査
#

# ファイルに含まれる道の数の調査
def count_road(file) :
    r_cnt = 0
    with open(file) as f:
        for line in f:
            # 文字列LineStringが含まれていたら道と判断
            if "LineString" in line :
                r_cnt = r_cnt + 1
    return r_cnt

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

# 入力ファイル
kml_files = ["./data/od_gis_10121_kokudo.kml", "./data/od_gis_10122_kendo.kml", "./data/od_gis_10123_shido.kml"]

# 道の数の調査
for file in kml_files :
    print(count_road(file))
