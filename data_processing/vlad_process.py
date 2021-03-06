from scipy.cluster.vq import vq, kmeans
from numpy import zeros, subtract, add, ndarray, savetxt, asarray, append
from utility import read_feature_vector, list_all_files
from window_process import get_win_label
from kmeans.kmeans import mykmeans_plus

def learn_vocabulary(k, max_iter, single_file, vector_matrix=None, input_path=None):
    if vector_matrix is None:
        if single_file:
            vector_matrix = read_feature_vector(input_path)
        else:
            file_names = list_all_files(input_path)
            vector_matrix = read_feature_vector(input_path + file_names[0])
            for f in xrange(1, len(file_names)):
                vector = read_feature_vector(input_path + file_names[f])
                if vector is not None:
                    vector_matrix = append(vector_matrix, vector, axis=0)
    return mykmeans_plus(data=vector_matrix,k=k, max_iter=max_iter)[0]

def vlad_vector(vector_path, vocabulary):
    features = read_feature_vector(vector_path)
    codes_idx = vq(features, vocabulary)[0] #A length M array holding the code book index for each observation
    vlad = zeros(vocabulary.shape) 
    for i in range(codes_idx.size):
        code_idx = codes_idx[i]
        diff = subtract(features[i], vocabulary[code_idx])
        vlad[code_idx] = add(diff, vlad[code_idx])
    return ndarray.flatten(vlad)
    
def vlad_vector_batch(input_path, output_path, vocabulary):
    vladL = []
    file_names = list_all_files(input_path)
    for f in file_names:
        vec = vlad_vector(vector_path=input_path + f, vocabulary=vocabulary)
        vladL.append(vec)
    output_path = output_path + '_vlad.txt'
    savetxt(output_path, asarray(vladL), delimiter=",", fmt='%.4f')
    
def get_data_set_X_Y(winL, vladL, pic, target, overlap_threshold):
        # Given the data of windows and VLAD of a given image
        # return the concatenated VLAD vector as X, and the label of windows as Y
        # X and Y should be the same length
        X, Y = [], []
        posWinSet, negWinSet = set([]), set([])
        for i in xrange(len(winL)):
            posWinSet.add(i) if get_win_label(p=pic, w=winL[i],
                target=target, threshold=overlap_threshold) else negWinSet.add(i)
        for i in posWinSet:
            s = ','.join([str(v) for v in vladL[i]])
            X.append(s), Y.append('1')
        for i in negWinSet:
            s = ','.join([str(v) for v in vladL[i]])
            X.append(s), Y.append('-1')
        X.append(''), Y.append('')
        return ('\n'.join(X), '\n'.join(Y))
