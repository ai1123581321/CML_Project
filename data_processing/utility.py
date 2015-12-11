from os import listdir, remove
from os.path import isfile, join, exists, getsize
from numpy import loadtxt, reshape, savetxt
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
    # By default, only files will be returned
    return [ f for f in listdir(input_path) if isfile(join(input_path, f)) and f.find('.') > 0]
        
def read_feature_vector(file_path):
    # Read feature properties and return in matrix form, 
    # i.e. 4 feature locations and 128 descriptors
    f = loadtxt(file_path)
    if len(f.shape) > 1:
        return f[:, 4:]
    if len(f.shape) == 1:
        return reshape(f[4:], (-1, 128))
    return None 

def get_unprocessed_images(log_path, all_image_path):
    log_List = set(list_all_files(log_path, onlyDir=True))
    all_images_List = list_all_files(all_image_path, onlyImage=True)
    unprocess_list = []
    for img in all_images_List:
        if img[:-4] not in log_List:
            unprocess_list.append(img)
    return unprocess_list

def delete_file(file_path, isDir=False):
    if exists(file_path):
        if isDir:
            shutil.rmtree(file_path)
        else:
            remove(file_path)

def append_file(dest_file, input_path=None, isSingleFile=False, strInput=None):
    dest_f = open(dest_file, "a")
    if strInput is not None:
        dest_f.write(strInput)
    elif input_path is not None:
        if isSingleFile:
            fin = open(input_path, "r")
            dest_f.write(fin.read())
            fin.close()
        else:  
            all_file_list = list_all_files(input_path=input_path)
            for file_name in all_file_list:
                fin = open(input_path + file_name, "r")
                dest_f.write(fin.read())
                fin.close()
    dest_f.close()
    
def get_target_pos_names(input_path, target, target_count=None):
    # input_path = "/Users/Kun/Desktop/CML_Project/sample/VOCdevkit/ImageSets/Main/"
    # target = "sheep"
    pos_list = []
    target_path = '%s%s_train.txt' % (input_path, target)
    i = 0
    with open(target_path) as f:
        for line in f:
            line = line.split()
            if line[1] == '1':
                pos_list.append(line[0])
                i += 1
                if target_count is not None and i == target_count:
                    return pos_list
    return pos_list

def save_matrix(v, output_path):
    savetxt(fname=output_path, X=v, fmt='%0.4f', delimiter=',', newline='\n')

def load_matrix(input_path):
    return loadtxt(fname=input_path, delimiter=',')
