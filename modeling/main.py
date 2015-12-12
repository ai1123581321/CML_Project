from sklearn import decomposition
import numpy as np

train = np.random.rand(1050, 4096)
test = np.random.rand(50, 4096)
print train.shape
print test.shape

pca = decomposition.PCA()
pca.n_components = 399
train_reduced = pca.fit_transform(train)
print train_reduced.shape
test_reduced = pca.transform(test)
print test_reduced.shape
