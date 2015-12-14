from xml.etree import ElementTree
from entity import Picture, Object
from utility import is_obj_valid, list_all_files, delete_file
from PIL import Image, ImageDraw
from os import system, makedirs
from os.path import exists

obj_para_list = ['name', 'truncated', 'difficult', 'xmin', 'ymin', 'xmax', 'ymax']
pic_para_list = ['width', 'height', 'img_id']
obj_para_map = dict((p, None) for p in obj_para_list)
pic_para_map = dict((p, None) for p in pic_para_list)

def parse_image_metadata(file_path, parseObject=False):
    DOMTree = ElementTree.parse(file_path)
    # First parse the img_id, width and height of an Image
    filename = DOMTree.find('filename').text
    pic_para_map['img_id'] = filename[:filename.rfind('.')]
    for size in DOMTree.find('size').iter():
        pic_para_map[size.tag] = size.text if size.tag in pic_para_map else None
    pic = Picture(img_id=pic_para_map['img_id'], width=pic_para_map['width'], height=pic_para_map['height'])
    if parseObject:
        # Otherwise, only need the width and height of the picture
        for obj in DOMTree.iter('object'):
            for o in obj.iter():
                obj_para_map[o.tag] = o.text if o.tag in obj_para_map else None
            if is_obj_valid(obj_para_map):
                pic.obj_set.add(Object(name=obj_para_map['name'], xmin=obj_para_map['xmin'],
                    ymin=obj_para_map['ymin'], xmax=obj_para_map['xmax'], ymax=obj_para_map['ymax']))
    return pic

def sift_image(input_path, image_name, output_path, params):
    # Process an image and save the results in a file, 
    # by using the sift exe file with command lines,
    image_path = input_path + image_name
    params = "--edge-thresh 10 --peak-thresh 5" if params is None else params
    file_extension = image_name[image_name.rfind('.') + 1:]
    image_name = image_name[:image_name.rfind('.')]
    if file_extension != 'pgm':
        # create a pgm file
        im = Image.open(image_path).convert('L')
        image_path = '%s%s.pgm' % (input_path, image_name)
        im.save(image_path)
    result_path = "%s%s_sift.txt" % (output_path, image_name)
    if not exists(output_path):
        makedirs(output_path)
    cmmd = "./sift %s -o %s %s" % (image_path, result_path, params)
    system(cmmd)
    delete_file(image_path)
    return result_path

def sift_image_batch(input_path, output_path, params=None):
    # Process all images in the input_path by SIFT, e.g. windows processing
    # Return those images whose SIFT vector is invalid, i.e. empty
    image_names = list_all_files(input_path, onlyImage=True)
    res_path_L = []
    for img in image_names:
        res_path = sift_image(input_path=input_path, image_name=img, output_path=output_path, params=params)
        res_path_L.append(res_path)
    return res_path_L

def draw_windows_on_image(img_obj, windowL, color):
    for win in windowL:
        bbox = (win.xmin, win.ymin, win.xmax, win.ymax)
        draw = ImageDraw.Draw(img_obj)
        draw.rectangle(bbox, outline=color)
        del draw
