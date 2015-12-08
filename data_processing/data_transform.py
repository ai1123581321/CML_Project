from xml.etree import ElementTree
from entity import Picture, Window, Object
from data_validation import is_obj_valid, check_win_boundary, update_win_label
from io_manager import crop_window

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
    image_path = input_path + image_name + '.jpg'
    windows = exhaustive_search(image_path, metadata_path, target, unit_ratio_list)
    winIndex = 0
    for win in windows:
        win.index = winIndex
        winIndex += 1
        crop_window(image_path, output_path, win=win, output_name='%s.jpeg' % str(winIndex))
    

def test1():
    image_name = "000012"
    file_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/Annotations/%s.xml" % image_name
    image_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/JPEGImages/%s.jpg" % image_name
    output_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/test.jpeg"
    pic = parse_image_metadata(file_path, target_name="chair")
    print pic
    # obj = pic.obj_set.pop()
    # print obj
    # crop_window(image_path, output_path, obj.xmin, obj.ymin, obj.xmax, obj.ymax)
    print check_win_boundary(pic, 450, 222)

def test2():
    p = Picture('test', 500, 200)
    window_builder(p, 0.2)
    
def test3():
    image_name = "000005"
    file_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/Annotations/%s.xml" % image_name
    image_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/JPEGImages/%s.jpg" % image_name
    exhaustive_search(image_path, file_path, target='chair', unit_ratio_list=[0.2, 0.3])
def test4():
    image_name = "000005"
    metadata_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/Annotations/%s.xml" % image_name
    input_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/JPEGImages/"
    output_path = "/Users/Kun/Desktop/CML_Project/VOCdevkit/windows/%s/" % (image_name)
    generate_image_window(input_path, image_name, metadata_path, 'chair', [0.2, 0.3, 0.4, 0.5], output_path)


test4()
