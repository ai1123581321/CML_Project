from xml.etree import ElementTree
from entity import Picture, Object
from utility import is_obj_valid, get_all_files, read_feature_vector
from PIL import Image
from os import system
from scipy.cluster.vq import vq
from numpy import zeros, subtract, add, ndarray, savetxt, asarray

obj_para_list = ['name', 'truncated', 'difficult', 'xmin', 'ymin', 'xmax', 'ymax']
pic_para_list = ['width', 'height', 'img_id']
obj_para_map = dict((p, None) for p in obj_para_list)
pic_para_map = dict((p, None) for p in pic_para_list)
win_para_map = dict((p, None) for p in [])

def parse_image_metadata(file_path, target_name):
    DOMTree = ElementTree.parse(file_path)
    # First parse the img_id, width and height of an Image
    pic_para_map['img_id'] = DOMTree.find('filename').text
    for size in DOMTree.find('size').iter():
        pic_para_map[size.tag] = size.text if size.tag in pic_para_map else None
    pic = Picture(img_id=pic_para_map['img_id'], width=pic_para_map['width'], height=pic_para_map['height'])
    for obj in DOMTree.iter('object'):
        for o in obj.iter():
            obj_para_map[o.tag] = o.text if o.tag in obj_para_map else None
        if is_obj_valid(obj_para_map, target_name):
            pic.obj_set.add(Object(name=obj_para_map['name'], xmin=obj_para_map['xmin'],
                ymin=obj_para_map['ymin'], xmax=obj_para_map['xmax'], ymax=obj_para_map['ymax']))
    return pic

def sift_image(input_path, image_name, output_path, params):
    # Process an image and save the results in a file, 
    # by using the sift exe file with command lines,
    # return the sift format text file
    params = "--edge-thresh 10 --peak-thresh 5" if params is None else params
    if image_name[-3:] != 'pgm':
        # create a pgm file
        im = Image.open(image_name).convert('L')
        image_name += '.pgm'
        im.save(image_name)
    result_path = "%s%s.txt" % (output_path, image_name)
    cmmd = "./sift %s%s -o %s %s" % (input_path, image_name, result_path, params)
    system(cmmd)
    return result_path

def sift_image_batch(input_path, output_path, params):
    # Process all images in the input_path by SIFT, e.g. windows processing
    image_names = get_all_files(input_path)
    res_path_L = []
    for img in image_names:
        im_path = '%s%s.jpg' % (input_path , img)
        temp_vlad_path = '%s%s/temp_vlad' % (output_path, img)
        res_path = sift_image(input_path=im_path, img, output_path=temp_vlad_path, params)
        res_path_L.append(res_path)
    return res_path_L

def vlad_vector(vector_path, vocabulary):
    features = read_feature_vector(vector_path)[1]
    codes = vq(features, vocabulary)[0]
    vlad = zeros(vocabulary.shape)
    for idx in range(codes.size):
        diff = subtract(features[idx], vocabulary[codes[idx]])
        vlad[codes[idx]] = add(diff, vlad[codes[idx]])
    return ndarray.flatten(vlad)
    
def vlad_vector_batch(input_path, output_path, vocabulary):
    # input_path = output/00005/temp_vlad/
    vladL = []
    vector_names = get_all_files(input_path)
    for vec in vector_names:
        vladL.append(vlad_vector(vector_path=vec, vocabulary=vocabulary))
    output_path = output_path + '_vlad.txt'
    savetxt(output_path, asarray(vladL), delimiter=",")
    return output_path






    