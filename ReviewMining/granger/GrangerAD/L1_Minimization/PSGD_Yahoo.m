function [w] = PSGD_Yahoo(X, y, eta, lambda, detail)
% Parallel stochastic gradient descent method to solve L1 regularized
% regression: (Xw-y)'(Xw-y) + lambda*|w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% eta: update step size
% lambda: regularization term
% detail: show details (1) or not (0)

%------------remove this!
% [N,~] = size(X);
% if N >= 80*8
% 	perm = sort(randperm(N,80*8));
% else
% 	perm = 1:N;
% end
% w = mex_PSGD_Yahoo(X(perm,:), y(perm), eta, lambda, detail);
%----------------------------

w = mex_PSGD_Yahoo(X, y, eta, lambda, detail);

end