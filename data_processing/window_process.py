from entity import Window
from utility import computeOverlap, check_win_boundary
from io_manager import crop_window, save_window_csv
from image_process import parse_image_metadata

def update_win_label(p, w, threshold=0.5):
    # Given a picture instance, assuming it has more than one valid object
    # update the window's label by calculating the overlap rate of window and objects in picture
    max_overlap_rate = 0
    for obj in p.obj_set:
        obj_area = (obj.ymax - obj.ymin) * (obj.xmax - obj.xmin)
        overlap = computeOverlap(A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax,
                            E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax)
        new_rate = (overlap * 1.0) / obj_area
        max_overlap_rate = new_rate if new_rate > max_overlap_rate else max_overlap_rate
    w.y_true = 1 if max_overlap_rate >= threshold else -1

def window_builder(picture, unit_ratio, overlap_ratio=None, winList=None):
    # Given a Picture instance, plus the unit_ratio and overlap_ratio of Window, 
    # build a list of candidate windows' boundary
    w = picture.width
    h = picture.height 
    winList = [] if winList is None else winList
    # Pick up the smaller one as the unit width of windows to as to get as many windows as possible
    win_width = int(w * unit_ratio) if w < h else int(h * unit_ratio)
    # Overlap among each square with ratio, if None then no overlap
    overlap = win_width * overlap_ratio if overlap_ratio is not None else win_width
    xmin, ymin, xmax, ymax = 0, 0, win_width, win_width
    while check_win_boundary(p=picture, w_xmax=xmax, w_ymax=ymax):
        while check_win_boundary(p=picture, w_xmax=xmax, w_ymax=ymax):
            win = Window(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
            update_win_label(p=picture, w=win)
            winList.append(win)
            ymin += overlap
            ymax += overlap
        xmin += overlap
        xmax += overlap
        ymin, ymax = 0, win_width
    return winList

def exhaustive_search(image_path, metadata_path, target, unit_ratio_list, overlap_ratio=None):
    picture = parse_image_metadata(metadata_path, target_name=target)
    picture.image_path = image_path
    windowL = []
    if len(picture.obj_set) > 0:
        for ratio in unit_ratio_list:
            window_builder(picture, unit_ratio=ratio, overlap_ratio=overlap_ratio, winList=windowL)
    return windowL

def generate_image_window(input_path, image_name, metadata_path, target, unit_ratio_list, output_path):
    # Given an image, generate all possible windows with the target
    image_path = input_path + image_name + '.jpg'
    windows = exhaustive_search(image_path, metadata_path, target, unit_ratio_list)
    winIndex = 0
    for win in windows:
        winIndex += 1
        win.index = winIndex
        crop_window(image_path, output_path, win=win, output_name='%s.jpeg' % str(winIndex))
    return windows

def test4():
    image_name = "000005"
    metadata_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/Annotations/%s.xml" % image_name
    input_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/JPEGImages/"
    output_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/windows/%s/" % (image_name)
    windows = generate_image_window(input_path, image_name, metadata_path, 'chair', [0.2, 0.3, 0.4, 0.5], output_path)
    save_window_csv(windows, output_path, image_name)


test4()
