function [w] = PStocSubGD_ref(X, y, ref_w, eta, lambda, maxIter, method, detail)
% Parallel stochastic gradient descent method to solve L1 regularized
% regression with coefficient similarity : (Xw-y)'(Xw-y) + lambda*|w-ref_w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% ref_w: reference coefficients
% eta: update step size
% lambda: regularization term
% maxIter: max number of iterations
% method: 0 for sequential stochSubGD; 1 for parallel stochSubGD.
% detail: show details (1) or not (0)

y_new = y - X*ref_w;
gama = mex_PStocSubGD(X, y_new, eta, lambda, maxIter, method, detail);
w = gama + ref_w;

end