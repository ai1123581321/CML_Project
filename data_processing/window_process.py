from entity import Window
from utility import computeOverlap, check_win_boundary
from image_process import parse_image_metadata

def get_win_label(p, w, threshold=0.5):
    # Given a picture instance, assuming it has more than one valid object
    # update the window's label by calculating the overlap rate of window and objects in picture
    max_overlap_rate = 0
    for obj in p.obj_set:
        obj_area = (obj.ymax - obj.ymin) * (obj.xmax - obj.xmin)
        overlap = computeOverlap(A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax,
                            E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax)
        new_rate = (overlap * 1.0) / obj_area
        max_overlap_rate = new_rate if new_rate > max_overlap_rate else max_overlap_rate
    return 1 if max_overlap_rate >= threshold else -1

def window_builder(p, unit_ratio, overlap_ratio, winList):
    # Given a Picture instance, plus the unit_ratio and overlap_ratio of Window, 
    # build a list of candidate windows' boundary
    w = p.width
    h = p.height
    winList = [] if winList is None else winList
    # Pick up the smaller one as the unit width of windows to as to get as many windows as possible
    win_width = int(w * unit_ratio) if w < h else int(h * unit_ratio)
    # Overlap among each square with ratio, if None then no overlap
    # Overlap_ratio
    overlap = w * overlap_ratio if overlap_ratio is not None else win_width
    xmin, ymin, xmax, ymax = 0, 0, win_width, win_width
    while check_win_boundary(w=w, h=h, w_xmax=xmax, w_ymax=ymax):
        while check_win_boundary(w=w, h=h, w_xmax=xmax, w_ymax=ymax):
            win = Window(index=len(winList) + 1, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
            winList.append(win)
            ymin += overlap
            ymax += overlap
        xmin += overlap
        xmax += overlap
        ymin, ymax = 0, win_width
    return winList

def exhaustive_search(image_path, metadata_path, unit_ratio_list, overlap_ratio):
    # Given an image and its annotation meta data, generate all possible windows with the target
    p = parse_image_metadata(metadata_path, parseObject=False)
    windowL = []
    for ratio in unit_ratio_list:
        window_builder(p=p, unit_ratio=ratio, overlap_ratio=overlap_ratio, winList=windowL)
    return windowL
