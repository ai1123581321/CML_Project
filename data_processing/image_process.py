from xml.etree import ElementTree
from entity import Picture, Object
from data_processing.utility import is_obj_valid

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
