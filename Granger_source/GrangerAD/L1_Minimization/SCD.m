function [w] = SCD(X, y, lambda, loss_type, maxIter, detail)
% Stochastic coordinate descent method to solve L1 regularized
% regression: (Xw-y)'(Xw-y) + lambda*|w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% lambda: regularization term
% loss_type: 0 for logistic, 2 for squared (default = 0)
% maxIter: max number of iterations
% detail: show details (1) or not (0)

% % normalize X and y:
% X = X / max(max(abs(X)));
% y = y / max(abs(y));

w = mex_SCD(X, y, lambda, loss_type, maxIter, detail);

end