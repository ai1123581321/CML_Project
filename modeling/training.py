from sklearn.cross_validation import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from sklearn.linear_model import SGDClassifier
import numpy as np
from data_processing.utility import list_all_files

def training(X_path, y_path, clf):
    X = np.loadtxt(fname=X_path, delimiter=',')
    y = np.loadtxt(fname=y_path, delimiter=',')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_state=42)
    clf = clf.fit(X_train, y_train)
    # print clf.coef_
    y_pred = clf.predict(X_test)
    print classification_report(y_test, y_pred)
    print clf.score(X=X_train, y=y_train)
    return clf

def cal_window_score(w, vlad_path, window_path):
    vlad_vec = np.loadtxt(fname=vlad_path, delimiter=',')
    score = np.dot(vlad_vec, w.T).flatten()
    index = score.argsort()
    print index[-3:][::-1] + 1
    print index[0:3][::-1] + 1
    print 'max=', np.argmax(score) + 1
    print 'min=', np.argmin(score) + 1
    # win = np.loadtxt(fname=window_path, delimiter=',')
    
input_parent_path = "/Users/Kun/Desktop/Project_CML/sample/output/sheep/"
X_path = input_parent_path + "global_X.txt"
y_path = input_parent_path + "global_y.txt"
clf = training(X_path, y_path, LinearSVC())

img_list = list_all_files(input_path=input_parent_path, onlyDir=True)
for img_name in img_list:
    print img_name, '=========='
    vlad_path = input_parent_path + "%s/%s_vlad.txt" % (img_name, img_name)
    window_path = input_parent_path + "%s/%s_windows.txt" % (img_name, img_name)
    cal_window_score(clf.coef_, vlad_path=vlad_path, window_path=window_path)
