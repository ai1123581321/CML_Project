import numpy as np
from generate_data import dataset_fixed_cov

def huber_loss(w, x, y, h):
    '''compute the huber loss for each training sample'''
    yt = np.dot(y, np.dot(x, w))
    if yt > 1+h:
        return 0
    elif yt < 1-h:
        return 1-yt
    else:
        return np.power(1+h-yt, 2)/(4*h)
     
def compute_obj(w, X_train, y_train, C=1, h=0.3):
    '''compute the overall cost based on huber loss for all training samples'''
    n_samples = X_train.shape[0]
    cost_list = np.zeros(n_samples)
    for i in xrange(n_samples):
        cost_list[i] = huber_loss(w, X_train[i], y[i], h)
    
    return np.dot(w, w) + C*np.mean(cost_list)


def huber_grad(w, x, y, h):
    '''compute the huber gradient for each training sample'''
    yt = np.dot(y, np.dot(x, w))
    if yt > 1+h:
        return np.zeros(x.shape[1])
    elif yt <1-h:
        return -y*x
    else:
        return -2*y*(1+h-yt)*x/(4*h)
    
    
def compute_grad(w, X_train, y_train, C=1, h=0.3):
    '''compute the overall huber gradient for all training samples'''
    n_samples, n_features = X.shape
    grad = 2*w
    for i in xrange(n_samples):
        grad += huber_grad(w, X_train[i], y[i], h)
            
    return grad / n_samples

def grad_checker(w, X, y, epsilon=0.01, tolerance=1e-4): 
    
    num_features = X.shape[0]
    true_gradient = compute_obj(X, y, w)
    
    approx_grad = np.zeros(num_features) 
    for i in np.arange(num_features):
        e = np.zeros(num_features)
        e[i] = epsilon
        approx_grad[i]=(compute_obj(X, y, w+e) - compute_obj(X, y, w-e))/(2*epsilon)
    
    dist = np.linalg.norm(approx_grad-true_gradient)
    
    return dist <= tolerance

# some tests
if __name__ == "__main__":
    X, y = dataset_fixed_cov(5)
    w = np.array([1,-1])
    print compute_obj(w, X, y, C=1, h=0.3)
    print compute_grad(w, X, y, C=1, h=0.3)
    # print grad_checker(w, X, y)
