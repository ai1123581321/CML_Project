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

def train_clf(X_path, y_path, clf, isScale=False, balanced=False):
    X = np.loadtxt(fname=X_path, delimiter=',')
    y = np.loadtxt(fname=y_path, delimiter=',')
    if isScale:
        print "\tScaling data set X"
        X = scale_dataset_X(X)
    if balanced:
        print "\tBalancing data set"
        X, y = balance_dataset(X, y)
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
    
def batch_training_display(input_parent_path, X_path, y_path,
            annotation_path, img_parent_path, target, topn, clf, threshold, img_output_path=None):
    print "Training classifier..."
    clf = train_clf(X_path, y_path, clf)
    img_list = list_all_files(input_path=input_parent_path, onlyDir=True)
    for img_name in img_list:
        print img_name, '=========='
        vlad_path = input_parent_path + "%s/%s_vlad.txt" % (img_name, img_name)
        window_path = input_parent_path + "%s/%s_windows.txt" % (img_name, img_name)
        if not exists(window_path):
            continue
        windowL = de_serialize_window(input_path=window_path)
        max_i, min_i = cal_window_score(clf.coef_, vlad_path=vlad_path, window_path=window_path, topn=topn)
        img_path = img_parent_path + img_name + ".jpg"
        pic = parse_image_metadata(file_path=annotation_path + img_name + ".xml", parseObject=True)
        win_label = window_display(img_path, windowL, max_i, min_i, 'blue', 'red',
                    pic, target, threshold, output_path=img_output_path, img_name=img_name)
        print "max label=", win_label[0], "min_label", win_label[1]
