from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
import numpy as np
from data_processing.window_process import get_win_label, de_serialize_window
from data_processing.image_process import draw_windows_on_image, parse_image_metadata
from data_processing.utility import list_all_files 


def train_clf(X_path, y_path, clf):
    X = np.loadtxt(fname=X_path, delimiter=',')
    y = np.loadtxt(fname=y_path, delimiter=',')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_state=42)
    clf = clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print classification_report(y_test, y_pred)
    print "score=", clf.score(X=X_train, y=y_train), '\n'
    return clf

def cal_window_score(w, vlad_path, window_path, topn=3):
    # Return the N windows with topn scores, either ascending or descending order
    vlad_vec = np.loadtxt(fname=vlad_path, delimiter=',')
    score = np.dot(vlad_vec, w.T).flatten()
    score_sort = score.argsort()
    max_index = score_sort[-topn:][::-1] + 1
    min_index = score_sort[0:topn][::-1] + 1
    print "max=", max_index, "min=", min_index
    return max_index, min_index
    
def window_display(img_path, windowL, indexL, pic, target, threshold, color):
    targetW = [ windowL[i - 1] for i in indexL]
    labelW = []
    for w in targetW:
        labelW.append(get_win_label(w=w, p=pic, target='sheep', threshold=0.5))
    draw_windows_on_image(input_path=img_path, color=color, windowL=targetW, img_name=img_path)
    return labelW

def batch_training_display(input_parent_path, X_path, y_path,
            annotation_path, img_parent_path, target, clf, threshold):
    print "Training classifier..."
    clf = train_clf(X_path, y_path, clf)
    img_list = list_all_files(input_path=input_parent_path, onlyDir=True)
    for img_name in img_list[3:6]:
        print img_name, '=========='
        vlad_path = input_parent_path + "%s/%s_vlad.txt" % (img_name, img_name)
        window_path = input_parent_path + "%s/%s_windows.txt" % (img_name, img_name)
        windowL = de_serialize_window(input_path=window_path)
        max_i, min_i = cal_window_score(clf.coef_, vlad_path=vlad_path, window_path=window_path)
        img_path = img_parent_path + img_name + ".jpg"
        pic = parse_image_metadata(file_path=annotation_path + img_name + ".xml", parseObject=True)
        max_label = window_display(img_path, windowL, max_i, pic, target, threshold, color='blue')
        min_label = window_display(img_path, windowL, min_i, pic, target, threshold, color='red')
        print "max label=", max_label, "min_label", min_label
