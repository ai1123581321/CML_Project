from sklearn.linear_model import SGDClassifier
from training import batch_training_display

working_dir = "/Users/Kun/Desktop/Project_CML/"
annotation_path = working_dir + "Annotations/"
img_parent_path = working_dir + "JPEGImages/"
target = "bicycle"
input_parent_path = working_dir + "output/" + target + "/"
X_path = input_parent_path + "global_X.txt"
y_path = input_parent_path + "global_y.txt"
threshold = 0.5
k = 5
topn = 3
isScale = False
balanced = False
weighted = False
class_weight = 'balanced' if weighted else None
suffix = 'balanced' if balanced else '' 
if class_weight: suffix += 'weighted'  
if isScale: suffix += 'scaled' 
file_suffix = 'k%s_%s' % (str(k), suffix)
log_path = input_parent_path + 'log/log_%s.txt' % file_suffix
windows_output_path = input_parent_path + 'windows_trained/trained_%s/' % file_suffix
clf = SGDClassifier(class_weight=class_weight) 

batch_training_display(input_parent_path, X_path, y_path,
        annotation_path, img_parent_path, target, topn, clf, threshold, windows_output_path,
        isScale, balanced, log_path)
