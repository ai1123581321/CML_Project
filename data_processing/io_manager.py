from os.path import isfile, join
from os import listdir
import os
from numpy import loadtxt
from PIL import Image

def get_all_image_name(input_path):
    # return a list of all images in the input path
    file_suffix = set(['jpg', 'png', 'pgm'])
    return [ f for f in listdir(input_path) 
            if isfile(join(input_path, f)) and f[f.rfind('.') + 1:] in file_suffix]
    
def read_feature_vector(filename):
    # Read feature properties and return in matrix form, 
    # i.e. feature locations and 128 descriptors
    f = loadtxt(filename)
    return f[:, :4], f[:, 4:]

def crop_window(input_path, output_path, output_name, win):
    im = Image.open(input_path)
    new_im = im.crop((win.xmin, win.ymin, win.xmax, win.ymax))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    new_im.save(output_path + output_name, 'JPEG')
    return True    