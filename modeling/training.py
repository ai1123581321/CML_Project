from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
import numpy as np
from data_processing.window_process import de_serialize_window, window_display
from data_processing.image_process import parse_image_metadata
from data_processing.utility import list_all_files, write_to_file, log_processing
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
    pos_scores = np.array([np.dot(vlad_vec[i], w.T) for i in pos_index])
    neg_scores = np.array([np.dot(vlad_vec[i], w.T) for i in neg_index])
    max_index = pos_scores.flatten().argsort()[-topn:][::-1]
    min_index = neg_scores.flatten().argsort()[0:topn][::-1]
    return max_index, min_index

def batch_training_display(input_parent_path, X_path, y_path,
            annotation_path, img_parent_path, target, topn, clf, threshold, windows_output_path=None,
            isScale=False, balanced=False, log_path=None):
    log_L = []
    log_processing(log_L, "Training classifier...")
    X = np.loadtxt(fname=X_path, delimiter=',')
    y = np.loadtxt(fname=y_path, delimiter=',')
    if isScale:
        log_processing(log_L, "\tScaling data set X")
        X = scale_dataset_X(X)
    if balanced:
        log_processing(log_L, "\tBalancing data set")
        X, y = balance_dataset(X, y)
    X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=20)
    clf = clf.fit(X_train, y_train)
    log_processing(log_L, classification_report(y_test, clf.predict(X_test)))
    y_pred = clf.predict(np.loadtxt(fname=X_path, delimiter=','))
    img_windows_path = input_parent_path + 'windows/'
    img_list = list_all_files(input_path=img_windows_path, onlyDir=True)
    vlad_offset = 0
    for img_name in img_list:
        vlad_path = img_windows_path + "%s/%s_vlad.txt" % (img_name, img_name)
        window_path = img_windows_path + "%s/%s_windows.txt" % (img_name, img_name)
        if not exists(window_path):
            continue
        log_processing(log_L, img_name + '==========')
        windowL = de_serialize_window(input_path=window_path)
        max_i, min_i = cal_window_score(w=clf.coef_, vlad_path=vlad_path,
                    y_pred=y_pred[vlad_offset: vlad_offset + len(windowL)], topn=topn)
        log_processing(log_L, "max pos=" + str(max_i) + ", min neg=" + str(min_i))
        vlad_offset += len(windowL)
        img_path = img_parent_path + img_name + ".jpg"
        pic = parse_image_metadata(file_path=annotation_path + img_name + ".xml", parseObject=True)
        win_label = window_display(img_path, windowL, max_i, min_i, 'blue', 'red',
                    pic, target, threshold, output_path=windows_output_path, img_name=img_name)
        log_processing(log_L, "max truth=" + str(win_label[0]) + ", min truth=" + str(win_label[1]))
    if log_path is not None:
        write_to_file(log_path, '\n'.join(log_L))
