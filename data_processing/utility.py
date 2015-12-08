def is_obj_valid(para_map, target_name):
    return para_map['name'] == target_name and para_map['truncated'] == '0' and para_map['difficult'] == '0'

def check_win_boundary(p, w_xmax, w_ymax):
    # Given a Picture instance, and a candidate window's 
    # coordinate values, check if the window is valid or not
    return p.width >= w_xmax and p.height >= w_ymax

def computeOverlap(A, B, C, D, E, F, G, H):
        # A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax
        # E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax
        if C < E or G < A or D < F or H < B:
            return 0
        return (min(C, G) - max(A, E)) * (min(H, D) - max(F, B))

