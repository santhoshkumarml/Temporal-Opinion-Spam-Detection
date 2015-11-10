function [w] = PStocSubGD(X, y, eta, lambda, maxIter, method, detail)
% Parallel stochastic gradient descent method to solve L1 regularized
% regression: (Xw-y)'(Xw-y) + lambda*|w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% eta: update step size
% lambda: regularization term
% maxIter: max number of iterations
% method: 0 for sequential stochSubGD; 1 for parallel stochSubGD.
% detail: show details (1) or not (0)

w = mex_PStocSubGD(X, y, eta, lambda, maxIter, method, detail);

end