function [w] = SCD_ref(X, y, ref_w, lambda, loss_type, maxIter, detail)
% Stochastic coordinate descent method to solve L1 regularized
% regression with coefficient similarity: (Xw-y)'(Xw-y) + lambda*|w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% ref_w: reference coefficients
% lambda: regularization term
% loss_type: 0 for logistic, 2 for squared (default = 0)
% maxIter: max number of iterations
% detail: show details (1) or not (0)

y_new = y - X*ref_w;
gama = mex_SCD(X, y_new, lambda, loss_type, maxIter, detail);
w = gama + ref_w;

end