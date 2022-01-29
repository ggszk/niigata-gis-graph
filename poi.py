#
# POIデータからのノード・エッジ作成
#

import common
from math import dist

# CSVファイルを読む，typeでノード・エッジ・POIを指定（0, 1, 2の値）
def read_csv(file, type) :
    list = []
    with open(file) as f:
        for line in f:
            l_list = line.split(',')
            if type == 0 : # ノード
                list.append((int(l_list[0]), float(l_list[1]), float(l_list[2])))
            elif type == 1 : # エッジ
                list.append((int(l_list[0]), int(l_list[1]), int(l_list[2])))
            elif type == 2 : # POI
                list.append((float(l_list[0]), float(l_list[1])))
            else :
                print("no such type")
                exit()
    return list

# CSV読み込みのテスト
def read_csv_test() :
#    list = read_csv("./output/nodes.txt", 0)
    list = read_csv("./output/edges.txt", 1)
#    list = read_csv("poi.txt", 2)
    print(list)

# CSVファイルを書く，typeでノード・エッジを指定（0, 1の値）
def write_csv(data, file, type) :
    with open(file, "w") as f:
        for d in data :
            if type == 0 : # ノード
                f.write(str(d[0]) + "," + str(d[1]) + "," + str(d[2]) + "\n")
            elif type == 1 : # エッジ
                f.write(str(d[0]) + "," + str(d[1]) + "," + str(d[2]) + "\n")

# CSV書き込みのテスト
def write_csv_test(data) :
    write_csv(data, "test.txt", 0)

# POIに最も近いエッジを求める：エッジとPOIに近い側の端点を示す値（1または2→エッジ内でのインデックス）の組みを返す
def get_nearest_edge(poi, edges_with_seg) :
    min_edge = None
    min = 100000000
    for e in edges_with_seg :
        # 端点0側の距離
        d0 = dist(poi, e[3][0])
        # 端点1側の距離
        d1 = dist(poi, e[3][1])
        # 短い方がPOIとエッジの距離
        if d0 < d1 :
            d = d0
            near_node = 1
        else :
            d = d1
            near_node = 2
        # ｄが最小であれば更新
        if d < min :
            min_edge = e
            min = d
    return (min_edge, near_node)

# 全体の実行
def main() :
    # 最初のノードID＝既に作成されている道路網の最大のノードID+1
    start_nid = 391224

    # 最初のエッジID＝既に作成されている道路網の最大のエッジID+1
    start_eid = 556970

    # CSVファイルの読み込み
    nodes = read_csv("./output/nodes.txt", 0)
    edges = read_csv("./output/edges.txt", 1)
    pois = read_csv("./input/poi.txt", 2)

    # エッジの情報に，座標の組み（線分）の情報を追加
    edges_with_seg = []

    for e in edges :
        from_n = nodes[e[1]]
        to_n = nodes[e[2]]
        from_p = (from_n[1], from_n[2])
        to_p = (to_n[1], to_n[2])

        e2 = (e[0], e[1], e[2], (from_p, to_p))
        edges_with_seg.append(e2)

    # POIとエッジの（近い方の）端点との間にエッジを作成する
    e_id = start_eid + 1
    poi_id = start_nid + 1
    
    out_nodes = []
    out_edges = []
    for poi in pois :
        # POIのノード作成
        n_poi = (poi_id, poi[0], poi[1])
        out_nodes.append(n_poi)

        (e, idx) = get_nearest_edge(poi, edges_with_seg)
        # POIへのエッジを作成
        e_poi = (e_id, e[idx], poi_id)
        e_id = e_id + 1
        poi_id = poi_id + 1

        out_edges.append(e_poi)
        
    write_csv(out_nodes, "./output/nodes_poi.txt", 0)  
    write_csv(out_edges, "./output/edges_poi.txt", 1)  
    
# サンプルグラフ(デバッグ用)
nodes = [
    (0,138.93704620065282,37.748195127472428),
    (1,138.93698747041839,37.748280945133466),
    (2,138.93687250370994,37.748220550338011),
    (3,138.93717352638038,37.748369549388315),
    (4,138.93723744607334,37.748278576391158),
    (5,138.9372139452386,37.74825739875147),
    (6,138.93719924876822,37.74822825919496),
    (7,138.93686657352265,37.748447186792852),
    (8,138.9369384526882,37.748474672737643),
    (9,138.9370062874215,37.748431891612043),
    (10,138.93707869862067,37.748414773446143),
    (11,138.93712504259045,37.748345310712885),
    (12,138.91180103569039,37.748874601123511),
    (13,138.91184073084608,37.748932039665526)
]

edges = [
    (0,0,1),
    (1,1,2),
    (2,3,4),
    (3,4,5),
    (4,5,6),
    (5,7,8),
    (6,8,9),
    (7,9,10),
    (8,10,11),
    (9,12,13)
]

# サンプルPOI
pois = [
    (138.9904,37.878876),
    (139.10106,37.885254),
    (138.99303,37.873913)
]

# 実行されるプログラム
#read_csv_test()
#write_csv_test(nodes)
main()
