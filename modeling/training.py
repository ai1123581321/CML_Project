from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
import numpy as np
from data_processing.window_process import de_serialize_window, window_display
from data_processing.image_process import parse_image_metadata
from data_processing.utility import list_all_files 
from os.path import exists
from sklearn.preprocessing import StandardScaler
from random import sample

def scale_dataset_X(X):
    scaler = StandardScaler()
    scaler.fit(X)
    return scaler.transform(X)
    
def balance_dataset(X, Y):
    pos_index, neg_index = [], []
    for i in xrange(len(Y)):
        if Y[i] == 1:
            pos_index.append(i)
        else:
            neg_index.append(i)
    neg_index = sample(neg_index, len(pos_index))
    X_balanced, Y_balanced = [X[i]for i in pos_index], [1] * len(pos_index)
    for i in neg_index:
        X_balanced.append(X[i])
        Y_balanced.append(-1)
    return X_balanced, Y_balanced  

def cal_window_score(w, vlad_path, y_pred, topn=3):
    # Return the N windows with topn scores, either ascending or descending order
    vlad_vec = np.loadtxt(fname=vlad_path, delimiter=',')
    pos_index, neg_index = [], []
    for i in xrange(len(vlad_vec)):
        pos_index.append(i) if (y_pred[i] == 1) else neg_index.append(i)
    pos_vlad_vec = [vlad_vec[i] for i in pos_index]
    # neg_vlad_vec = [vlad_vec[i] for i in neg_index]
    pos_vlad_vec, neg_vlad_vec = [], []
    for i in pos_index:
        score = np.dot(vlad_vec[i], w.T)
        pos_vlad_vec.append((i, score))
    neg_vlad_vec = [(vlad_vec[i], np.dot(vlad_vec[i], w.T)) for i in neg_index]
    # sorted_pos_vlad = sorted(pos_vlad_vec, key=lambda x: x[1])
    # sorted_neg_vlad = sorted(neg_vlad_vec, key=lambda x: x[1])
    pos_score = np.dot(pos_vlad_vec, w.T).flatten().argsort()
    neg_score = np.dot(neg_vlad_vec, w.T).flatten().argsort()
    max_index = pos_score[-topn:][::-1]
    min_index = neg_score[0:topn][::-1]
    print max_index, min_index
    print pos_score[max_index], neg_score[min_index]
    return max_index, min_index


def batch_training_display(input_parent_path, X_path, y_path,
            annotation_path, img_parent_path, target, topn, clf, threshold, img_output_path=None,
            isScale=False, balanced=False):
    print "Training classifier..."
    X = np.loadtxt(fname=X_path, delimiter=',')
    y = np.loadtxt(fname=y_path, delimiter=',')
    if isScale:
        print "\tScaling data set X"
        X = scale_dataset_X(X)
    if balanced:
        print "\tBalancing data set"
        X, y = balance_dataset(X, y)
    X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=20)
    clf = clf.fit(X_train, y_train)
    print classification_report(y_test, clf.predict(X_test))
    y_pred = clf.predict(np.loadtxt(fname=X_path, delimiter=','))
    img_list = list_all_files(input_path=input_parent_path, onlyDir=True)
    vlad_offset = 0
    for img_name in img_list:
        vlad_path = input_parent_path + "%s/%s_vlad.txt" % (img_name, img_name)
        window_path = input_parent_path + "%s/%s_windows.txt" % (img_name, img_name)
        if not exists(window_path):
            continue
        print img_name, '=========='
        windowL = de_serialize_window(input_path=window_path)
        max_i, min_i = cal_window_score(w=clf.coef_, vlad_path=vlad_path,
                    y_pred=y_pred[vlad_offset: vlad_offset + len(windowL)], topn=topn)
        print "max=", max_i, "min=", min_i
        vlad_offset += len(windowL)
        img_path = img_parent_path + img_name + ".jpg"
        pic = parse_image_metadata(file_path=annotation_path + img_name + ".xml", parseObject=True)
        win_label = window_display(img_path, windowL, max_i, min_i, 'blue', 'red',
                    pic, target, threshold, output_path=img_output_path, img_name=img_name)
        print "max truth=", win_label[0], "min truth=", win_label[1]
