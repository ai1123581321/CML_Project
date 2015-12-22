import sys, numpy as np
from collections import deque
from gradient_descent import misclass_error, misclass_validation, cal_average_W

def my_sgd(fun_obj, fun_grad, x_train, y_train, w0, eta0,
           t0, max_iter, stop_criterion=None, rho=0.9, obj_logs=None):
    w = w0
    wList = [np.array(w0)]
    i = 0
    stop = False
    t = 0
    perfQueue = deque()  # Use deque for the validation stop criteria
    while i < max_iter and not stop:
        rndIndex = np.random.permutation(len(x_train))
        j = 0
        while j < len(rndIndex) and not stop:
            k = rndIndex[j]
            x, y = x_train[k], y_train[k]  # x_train[k:(k+1), :], y_train[k]
            if obj_logs is not None:  # Used for warm up logging
                obj_logs.append(fun_obj(w=w, x_train=x, y_train=y))
            grad = fun_grad(w=w, x_train=x, y_train=y)
            t += 1
            w -= (eta0 / (t + t0)) * grad
            if stop_criterion == 'validation':
                pref = misclass_error(w, x_train, y_train)
                stop = misclass_validation(pref=pref, perfQueue=perfQueue, rho=rho)
            j += 1
        wList.append(w)
        i += 1
    return cal_average_W(wList)

def warm_up(fun_obj, fun_grad, x_train, y_train, max_iter, etaList=None, tList=None,
        w0=None, stop_criterion=None, rho=0.9):
    rndSize = 100 if 100 < len(x_train) else len(x_train)
    idx = np.random.choice(len(x_train), rndSize)
    x, y = x_train[idx], y_train[idx]
    etaList = [0.5, 0.1, 0.05, 0.001] if etaList is None else etaList
    tList = [1, 10, 20, 50, 100] if tList is None else tList
    obj_logs = []  # Used to record the objective value
    best_eta = None
    best_t = None
    min_score = -sys.maxint
    for eta0 in etaList:
        for t0 in tList:
            my_sgd(fun_obj=fun_obj, fun_grad=fun_grad, x_train=x, y_train=y, w0=w0, obj_logs=obj_logs,
            eta0=eta0, t0=t0, max_iter=max_iter, stop_criterion=stop_criterion, rho=rho)
            if obj_logs[-1] < min_score:
                min_score = obj_logs[-1]
                best_eta = eta0
                best_t = t0
    return best_eta, best_t

