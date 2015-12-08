def is_obj_valid(para_map, target_name):
    return para_map['name'] == target_name and para_map['truncated'] == '0' and para_map['difficult'] == '0'

def check_win_boundary(picture, w_xmax, w_ymax):
    # Given a Picture instance, and a candidate window's 
    # coordinate values, check if the window is valid or not
    return picture.width >= w_xmax and picture.height >= w_ymax

def update_win_label(p, w, threshold=0.5):
    def computeOverlap(A, B, C, D, E, F, G, H):
        # A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax
        # E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax
        if C < E or G < A or D < F or H < B:
            return 0
        return (min(C, G) - max(A, E)) * (min(H, D) - max(F, B))

    # Given a picture instance, assuming it has more than one valid object
    # update the window's label by calculating the overlap rate of window and objects in picture
    max_overlap_rate = 0
    for obj in p.obj_set:
        obj_area = (obj.ymax - obj.ymin) * (obj.xmax - obj.xmin)
        overlap = computeOverlap(A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax,
                            E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax)
        new_rate = (overlap * 1.0) / obj_area
        max_overlap_rate = new_rate if new_rate > max_overlap_rate else max_overlap_rate
    w.y_true = max_overlap_rate >= threshold
