from os import listdir, makedirs, remove
from os.path import isfile, join, exists, getsize
from PIL import Image
from numpy import loadtxt, reshape
import shutil

def is_non_zero_file(fpath):
    # check if a file is empty or not, used for SIFT result
    return True if isfile(fpath) and getsize(fpath) > 0 else False

def is_obj_valid(para_map):
    return para_map['truncated'] == '0' and para_map['difficult'] == '0'

def check_win_boundary(w, h, w_xmax, w_ymax):
    # Given a Picture instance, and a candidate window's 
    # coordinate values, check if the window is valid or not
    return w >= w_xmax and h >= w_ymax

def computeOverlap(A, B, C, D, E, F, G, H):
        # A=w.xmin, B=w.ymin, C=w.xmax, D=w.ymax
        # E=obj.xmin, F=obj.ymin, G=obj.xmax, H=obj.ymax
        if C < E or G < A or D < F or H < B:
            return 0
        return (min(C, G) - max(A, E)) * (min(H, D) - max(F, B))

def list_all_files(input_path, onlyImage=False, onlyDir=False):
    # return a list of all files in the input path
    if onlyImage:
        file_suffix = set(['jpg', 'png', 'pgm', 'jpeg'])
        return [ f for f in listdir(input_path) if isfile(join(input_path, f)) and f[f.rfind('.') + 1:] in file_suffix]
    if onlyDir:
        return [ f for f in listdir(input_path) if not isfile(join(input_path, f))]
    return [ f for f in listdir(input_path) if isfile(join(input_path, f)) and f.find('.') > 0]
        
def read_feature_vector(file_path):
    # Read feature properties and return in matrix form, 
    # i.e. 4 feature locations and 128 descriptors
    f = loadtxt(file_path)
    print file_path
    print f.shape
    if len(f.shape) > 1:
        return f[:, 4:]
    if len(f.shape) == 1:
        return reshape(f[4:], (-1, 128))
    return None 


def crop_window(input_path, output_path, windows):
    if not exists(output_path):
        makedirs(output_path)
    else:
        shutil.rmtree(output_path)
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

def save_window_txt(windows, output_path, image_name):
    # Save the meta data of all valid windows generated of a given image
    win_txt = image_name + '_windows.txt'
    win_file = output_path + win_txt
    if not exists(output_path):
        makedirs(output_path)
    win_file = open(win_file, "w")
    win_file.write(serialize_window(windows))
    win_file.close()

def get_unprocessed_images(log_path, all_image_path):
    log_List = set(list_all_files(log_path, onlyDir=True))
    all_images_List = list_all_files(all_image_path, onlyImage=True)
    unprocess_list = []
    for img in all_images_List:
        if img[:-4] not in log_List:
            unprocess_list.append(img)
    return unprocess_list

def delete_file(file_path, isDir=False):
    if isDir:
        shutil.rmtree(file_path)
    else:
        remove(file_path)

def validate_windows(input_windows, crop_path, sift_path):
    # Validate a window given the SIFT result of it
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
