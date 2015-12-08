from entity import Window
from utility import computeOverlap
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

def window_builder(picture, unit_ratio, overlap_ratio=None):
    # Given a Picture instance, plus the unit_ratio and overlap_ratio of Window, 
    # build a list of candidate windows' boundary
    w = picture.width
    h = picture.height 
    winList = []
    # Pick up the smaller one as the unit width of windows to as to get as many windows as possible
    win_width = int(w * unit_ratio) if w < h else int(h * unit_ratio)
    if overlap_ratio is None:
        for i in xrange(1, 1 + w / win_width):
            xmin = (i - 1) * win_width
            for j in xrange(1, 1 + h / win_width):
                ymin = (j - 1) * win_width 
                xmax, ymax = xmin + win_width, ymin + win_width
                win = Window(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
                update_win_label(p=picture, w=win)
                winList.append(win)
    return winList

def exhaustive_search(image_path, metadata_path, target, unit_ratio_list):
    picture = parse_image_metadata(metadata_path, target_name=target)
    picture.image_path = image_path
    windowL = []
    if len(picture.obj_set) > 0:
        for ratio in unit_ratio_list:
            windowL.extend(window_builder(picture, ratio))
    return windowL

def generate_image_window(input_path, image_name, metadata_path, target, unit_ratio_list, output_path):
    # Given an image, generate all possible windows with the target
    image_path = input_path + image_name + '.jpg'
    windows = exhaustive_search(image_path, metadata_path, target, unit_ratio_list)
    winIndex = 0
    for win in windows:
        win.index = winIndex
        winIndex += 1
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
