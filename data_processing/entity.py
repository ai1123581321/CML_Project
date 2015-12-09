class Object(object):
    def __init__(self, name, xmin, ymin, xmax, ymax):
        self.name = name
        self.xmin = int(xmin)
        self.ymin = int(ymin)
        self.xmax = int(xmax)
        self.ymax = int(ymax)
    
    def __repr__(self):
        return 'name=%s, xmin=%s, ymin=%s, xmax=%s, ymax=%s' % (self.name,
                        self.xmin, self.ymin, self.xmax, self.ymax)

class Picture(object):
    def __init__(self, img_id, width, height):
        self.img_id = img_id
        self.width = int(width)
        self.height = int(height)
        self.obj_set = set([])
        self.image_path = ""
    
    def __repr__(self):
        s = ['img_id=%s, width=%s, height=%s, valid objects:' % (self.img_id, self.width, self.height)]
        for obj in self.obj_set:
            s.append('\t' + str(obj))
        return '\n'.join(s)
 
class Window(object):
    def __init__(self, index, xmin, ymin, xmax, ymax):
        self.index = index
        self.xmin = int(xmin)
        self.ymin = int(ymin)
        self.xmax = int(xmax)
        self.ymax = int(ymax)
    
    def __repr__(self):
        return 'W(index=%s, xmin=%s, ymin=%s, xmax=%s, ymax=%s)' % (
                self.index, self.xmin, self.ymin, self.xmax, self.ymax)

