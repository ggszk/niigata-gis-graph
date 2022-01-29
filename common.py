#
# 共通に利用する関数
#

# 2点を通る直線の傾きと切片の組を返す
def get_line(p0, p1) :
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]

    # x座標が等しいときは少しずらす
    if x0 == x1 :
        x0 = x0 + 0.0000000000001
        
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
