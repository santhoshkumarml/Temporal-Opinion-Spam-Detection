function [w, tot_w, tot_obj] = SGLangDyn(X, y, lambda, batch_size, a, b, gamma, maxIter)
% stochastic gradient (subgradient) Langevin Dynamics

	if (~exist('a','var'))
		a = 1;
	end
	if (~exist('b','var'))
		b = 1;
	end
	if (~exist('gamma','var'))
		gamma = 0.55;
	end
	if (~exist('maxIter','var'))
		maxIter = 10000;
	end
	
	[N, D] = size(X);
	
	if (~exist('batch_size','var'))
		batch_size = N/2;
	end
	
	w = (X'*X + lambda*eye(D))\(X'*y);
	tot_w = w;
	tot_obj = (X*w-y)' * (X*w-y) + lambda * sum(abs(w));
	% iteration:
	for t = 1:maxIter
		batch_index = sort(randi([1, N], batch_size, 1));
		X_batch = X(batch_index, :);
		y_batch = y(batch_index);
		subgrad = N/batch_size * 2 * X_batch' * (X_batch*w-y_batch) + lambda * sign(w);
		
		step = a*(b+t)^(-gamma);
		noise = sqrt(step) * randn(D, 1);
		
		w = w - (step * subgrad + noise);
		
		if t > maxIter/4
			tot_w = [tot_w w];
			tot_obj = [tot_obj; (X*w-y)' * (X*w-y) + lambda * sum(abs(w))];
		end
	end
end




