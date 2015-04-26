function [w] = SGLD_ref(X, y, ref_w, a, b, gamma, lambda, batch_size, maxIter, detail)
% Parallel stochastic gradient descent method to solve L1 regularized
% regression with coefficient similarity: (Xw-y)'(Xw-y) + lambda*|w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% ref_w: reference coefficients
% eta = a*(b+t)^(-gamma)
% lambda: regularization term
% batch_size: batch size
% maxIter: max number of iterations
% detail: show details (1) or not (0)

[N,~] = size(X);
if batch_size > N
	batch_size = 1;
end

y_new = y - X*ref_w;
gama = mex_SGLD(X, y_new, a, b, gamma, lambda, batch_size, maxIter, detail);
w = gama + ref_w;

end