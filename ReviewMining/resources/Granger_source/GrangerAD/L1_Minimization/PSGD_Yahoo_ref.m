function [w] = PSGD_Yahoo_ref(X, y, ref_w, eta, lambda, detail)
% Parallel stochastic gradient descent method to solve L1 regularized
% regression with coefficient similarity to 'ref_w':
% (Xw-y)'(Xw-y) + lambda*|w-ref_w|_1
% X: design matrix, N-by-D
% y: labels (double), D-by-1
% ref_w: reference coefficients
% eta: update step size
% lambda: regularization term
% maxIter: max number of iterations
% detail: show details (1) or not (0)

%-------------remove this!
% [N,~] = size(X);
% if N >= 80*8
% 	perm = sort(randperm(N,80*8));
% else
% 	perm = 1:N;
% end
% y_new = y(perm) - X(perm,:)*ref_w;
% gama = mex_PSGD_Yahoo(X(perm,:), y_new, eta, lambda, detail);
% w = gama + ref_w;
% -----------------------------

y_new = y - X*ref_w;
gama = mex_PSGD_Yahoo(X, y_new, eta, lambda, detail);
w = gama + ref_w;

end