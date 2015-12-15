from entity import Window
from PIL import Image
from utility import computeOverlap, check_win_boundary, is_non_zero_file, delete_file
from image_process import parse_image_metadata, draw_windows_on_image
from os.path import exists
from os import makedirs
from shutil import rmtree
from datetime import datetime

def get_win_label(p, w, target, threshold):
    # Given a picture instance, assuming it has more than one valid object
    # update the window's label by calculating the overlap rate of window and objects in picture
    max_overlap_rate = 0
    for obj in p.obj_set:
        win_area = (w.ymax - w.ymin) * (w.xmax - w.xmin)
        overlap = computeOverlap(A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax,
                            E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax)
        new_rate = (overlap * 1.0) / win_area
        if new_rate > max_overlap_rate and obj.name == target:
            max_overlap_rate = new_rate
    return max_overlap_rate >= threshold

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

def crop_window(input_path, output_path, windows):
    if not exists(output_path):
        makedirs(output_path)
    else:
        rmtree(output_path)
    im = Image.open(input_path)
    for win in windows:
        new_im = im.crop((win.xmin, win.ymin, win.xmax, win.ymax))
        new_im_path = '%s%s.jpg' % (output_path, win.index)
        new_im.save(new_im_path, 'JPEG')

def serialize_window(windows):
    winL = ['index, xmin, ymin, xmax, ymax']
    i = 0
    for w in windows:
        wL = [w.index, w.xmin, w.ymin, w.xmax, w.ymax]
        wL = [str(i) for i in wL]
        winL.append(','.join(wL))
    return '\n'.join(winL)

def de_serialize_window(input_path):
    windowsL = []
    with open(input_path) as f:
        for line in f:
            lines = line.split(",")
            if len(lines) == 5 and lines[0] != 'index':
                win = Window(index=lines[0], xmin=lines[1], ymin=lines[2], xmax=lines[3], ymax=lines[4])
                windowsL.append(win)
    return windowsL

def save_window_txt(windows, output_path, image_name):
    # Save the meta data of all valid windows generated of a given image
    win_txt = image_name + '_windows.txt'
    win_file = output_path + win_txt
    if not exists(output_path):
        makedirs(output_path)
    win_file = open(win_file, "w")
    win_file.write(serialize_window(windows))
    win_file.close()

def validate_windows(input_windows, crop_path, sift_path):
    # Validate a window given the SIFT result of it
    # If the result is an empty SIFT file, it is invalid
    valid_windows = []
    for w in input_windows:
        i = str(w.index)
        sift_file = sift_path + i + '_sift.txt'
        if is_non_zero_file(fpath=sift_file):
            valid_windows.append(w)
        else:
            delete_file(sift_file)
            delete_file(crop_path + i + '.jpg')
    return valid_windows

def window_display(img_path, windowL, pos_index, neg_index, pos_color, neg_color,
                pic, target, threshold, output_path=None, img_name=None):
    posW = [windowL[i - 1] for i in pos_index]
    negW = [windowL[i - 1] for i in neg_index]
    posLabel = [get_win_label(w=w, p=pic, target='sheep', threshold=0.5) for w in posW]
    negLabel = [get_win_label(w=w, p=pic, target='sheep', threshold=0.5) for w in negW]
    img_obj = Image.open(img_path)
    draw_windows_on_image(img_obj=img_obj, color=pos_color, windowL=posW)
    draw_windows_on_image(img_obj=img_obj, color=neg_color, windowL=negW)
    if output_path is not None:
        if not exists(output_path):
            makedirs(output_path)
        img_obj.save(output_path + img_name + '.bmp', 'bmp')
    else:
        img_obj.show()
    return posLabel, negLabel
