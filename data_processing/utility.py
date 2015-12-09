from os import listdir, mkdir
from os.path import isfile, join, exists
from PIL import Image
from numpy import loadtxt


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

def get_all_files(input_path, isImage=True):
    # return a list of all files in the input path
    if isImage:
        file_suffix = set(['jpg', 'png', 'pgm', 'jpeg'])
        return [ f for f in listdir(input_path) 
            if isfile(join(input_path, f)) and f[f.rfind('.') + 1:] in file_suffix]
    else:
        return [ f for f in listdir(input_path)]
    
def read_feature_vector(file_path):
    # Read feature properties and return in matrix form, 
    # i.e. 4 feature locations and 128 descriptors
    f = loadtxt(file_path)
    return f[:, :4], f[:, 4:]

def crop_window(input_path, output_path, output_name, win):
    im = Image.open(input_path)
    new_im = im.crop((win.xmin, win.ymin, win.xmax, win.ymax))
    if not exists(output_path):
        mkdir(output_path)
    new_im.save(output_path + output_name, 'JPEG')
    return True    

def serialize_window_csv(windows):
    winL = ['index, xmin, ymin, xmax, ymax']
    for w in windows:
        wL = [w.index, w.xmin, w.ymin, w.xmax, w.ymax]
        wL = [str(i) for i in wL]
        winL.append(','.join(wL))
    return '\n'.join(winL)

def save_window_csv(windows, output_path, image_name):
    # Save the meta data of all windows generated of a given image
    win_txt = image_name + '_windows.csv'
    win_file = output_path + win_txt
    if not exists(output_path):
        mkdir(output_path)
    win_file = open(win_file, "w")
    win_file.write(serialize_window_csv(windows))
    win_file.close()
    return True
