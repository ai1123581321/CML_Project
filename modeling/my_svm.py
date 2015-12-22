import numpy as np
from gradient_descent import my_gradient_descent
from stoc_grad_descent import warm_up, my_sgd

def my_svm(x_train, y_train, fun_obj, fun_grad, w0=None, h=None,
           C=1, max_iter=1000, stepsize=0.5, isSGD=False, eta0=None, t0=None, rho=0.9,
           linesearch=False, stop_criterion=None, isWarmup=False, etaList=None, tList=None):
    w0 = np.zeros(len(x_train[0])) if w0 is None else w0
    if isSGD:  # stochastic gradient descent mode
        if isWarmup:  # warm-up with SGD mode
            eta0, t0 = warm_up(fun_obj=fun_obj, fun_grad=fun_grad, x_train=x_train,
            y_train=y_train, w0=w0, max_iter=max_iter, stop_criterion=stop_criterion,
            rho=rho, etaList=etaList, tList=tList)
        # Either case, return the stochastic gradient descent
        return my_sgd(fun_obj=fun_obj, fun_grad=fun_grad, x_train=x_train, y_train=y_train,
            w0=w0, eta0=eta0, t0=t0, max_iter=max_iter, stop_criterion=stop_criterion, rho=rho)
    return my_gradient_descent(x_train, y_train, w0, stepsize, max_iter, fun_obj, fun_grad)
