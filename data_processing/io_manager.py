import os, json
from numpy import loadtxt
from PIL import Image

def get_all_image_name(input_path):
    # return a list of all images in the input path
    file_suffix = set(['jpg', 'png', 'pgm'])
    return [ f for f in os.listdir(input_path) 
            if os.path.isfile(os.path.join(input_path, f)) and f[f.rfind('.') + 1:] in file_suffix]
    
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
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    win_file = open(win_file, "w")
    win_file.write(serialize_window_csv(windows))
    win_file.close()
    return True
