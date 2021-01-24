#
# 道と交点ファイルからノード・エッジデータを作成する
#

import json

# ノードデータの生成
def create_node(file, out_file):
    id = 0 # ノードid
    with open(out_file, "w") as o_f:
        with open(file) as f:
            for line in f:
                road = []
                coordinates = line.split()
                for c in coordinates :
                    o_f.write(str(id) + "," + c + "\n")
                    id = id + 1

# エッジデータの生成
def create_edge(file, out_file):
    n_id = 0 # ノードid
    e_id = 0 # エッジid
    with open(out_file, "w") as o_f:
        with open(file) as f:
            for line in f:
                road = []
                i = 1 # 座標の数のカウント用
                coordinates = line.split()
                for c in coordinates :
                    # 最後の座標ではエッジはつくられない
                    if i != len(coordinates) :
                        o_f.write(str(e_id) + "," + str(n_id) + "," + str(n_id + 1) + "\n")
                        e_id = e_id + 1
                    n_id = n_id + 1
                    i = i + 1
                i = 1

# 交点ノードの作成
def create_intersection_node(file, out_file, initial_node_id):
    id = initial_node_id # ノードid
    with open(out_file, "a") as o_f:
        with open(file) as f:
            for line in f:
                intersections = json.loads(line)
                for r in intersections :
                    for p in r[1] :
                        o_f.write(str(id) + "," + str(p[2][0]) + "," + str(p[2][1]) + "\n")
                        id = id + 1
    return

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
    
# 道ファイルにおける各行の先頭のノードidを求める
def get_node_ids(file) :
    roads = read_roads(file)
    ret = []
    id = 0
    for r in roads:
        ret.append(id)
        id = id + len(r)
    return ret

# 交点エッジの作成
def create_intersection_edge(file, out_file, initial_node_id, initial_edge_id, id_offset):
    n_id = initial_node_id # 交点のノードid
    e_id = initial_edge_id # エッジid
    l_id = 0 # 交点ファイルの行に相当するノードのid
    
    with open(out_file, "a") as o_f:
        with open(file) as f:
            for line in f:
                intersections = json.loads(line)
                for r in intersections :
                    to_l_id = r[0]
                    for p in r[1] :
                        # 交点に向かうエッジを作る
                        from_id = id_offset[l_id] + p[0]
                        to_id = n_id
                        o_f.write(str(e_id) + "," + str(from_id) + "," + str(to_id) + "\n")
                        e_id = e_id + 1
                        # 交点から出るエッジを作る
                        from_id = n_id
                        to_id = id_offset[to_l_id] + p[1]
                        o_f.write(str(e_id) + "," + str(from_id) + "," + str(to_id) + "\n")
                        e_id = e_id + 1
                        # 交点のノードidを一つ進める
                        n_id = n_id + 1
                l_id = l_id + 1
    return

initial_node_id = 206623
initial_edge_id = 187767

# 中間生成ファイルの置き場
temp_dir = "./result_temp/"

# 最終ファイルの置き場
out_dir = "./output/"

# ノード作成
create_node(temp_dir + "roads2.txt", out_dir + "nodes.txt")
create_intersection_node(temp_dir + "intersections.txt", out_dir + "nodes.txt", initial_node_id)

# 道ファイルにおける各行の先頭のノードidを求める
id_offset = get_node_ids(temp_dir + "roads2.txt") 

# エッジ作成
create_edge(temp_dir + "roads2.txt", out_dir + "edges.txt")
create_intersection_edge(temp_dir + "intersections.txt", out_dir + "edges.txt", initial_node_id, initial_edge_id, id_offset)