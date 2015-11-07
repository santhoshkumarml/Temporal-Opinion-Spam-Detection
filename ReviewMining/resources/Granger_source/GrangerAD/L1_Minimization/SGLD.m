function [w] = SGLD(X, y, a, b, gamma, lambda, batch_size, maxIter, detail)
% Parallel stochastic gradient descent method to solve L1 regularized
% regression: (Xw-y)'(Xw-y) + lambda*|w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% eta = a*(b+t)^(-gamma)
% lambda: regularization term
% batch_size: batch size
% maxIter: max number of iterations
% detail: show details (1) or not (0)

[N, ~] = size(X);
if batch_size > N
	batch_size = 1;
end

w = mex_SGLD(X, y, a, b, gamma, lambda, batch_size, maxIter, detail);

end