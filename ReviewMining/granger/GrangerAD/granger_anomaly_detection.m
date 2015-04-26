function [ref_coeffs, test_coeffs, anomaly_scores, anomaly_threshs] = ...
	granger_anomaly_detection(time_series, lag, ref_indices, test_indices, ...
	slide_times, alpha, lambda, lambda1, lambda2, NC)
% returns the coefficients on the reference data and test data, as well as
%		the anomaly scores between reference data and test data
% time_series: each time series forms a row of time_series
% lag: lag time
% ref_indices: column indices of time_series which form the reference time
%		series. e.g. ref_indices = 1:100, which means time_series(:, 1:100) are
%		used as reference data;
% test_indices: column indices of time_series which form the test time
%		series;
% slide_times: how many times to slide the test indices window; 0 if we
%		only work on one test data set;
% alpha: significance level for choosing anomaly thresholds. e.g. 0.95

% -N:
% lambda = 40;
% lambda1 = 40;
% lambda2 = 10;
% -C:
% lambda = 40;
% lambda1 = 10;
% lambda2 = 10;
%% process reference data
disp('training...');
ref_series = time_series(:, ref_indices);
[ref_coeffs, ~] = ts_lasso_regression(ref_series, lag, lambda);


%% compute anomaly thresholds for each time series
[p,T1] = size(ref_series);
anomaly_threshs = zeros(p, 1);
window_size = length(test_indices);
for i = 1:p
% 	pred_values = zeros(1, T1-lag);
% 	for j = 1:T1-lag
% 		pred_values(j) = sum(sum(ref_coeffs{i} .* ref_series(:, j:j+lag-1)));
% 	end
% 	resid = ref_series(i, lag+1:T1) - pred_values;
% 	sigma1 = sqrt(resid * resid' / length(resid));
	sigma1 = sqrt(var(ref_series(i,:)));
	
	ref_anomaly_scores = zeros(1, T1-window_size+1);
	for start = 1:T1-window_size+1
 		cur_ref_series = ref_series(:, start:start+window_size-1);
		
% 		[cur_ref_coeffs, cur_PHI] = ...
% 			ts_lasso_ref_regression(cur_ref_series, lag, lambda1, ref_coeffs, lambda2);
% 		
% 		[~, T2] = size(cur_ref_series);
% 		pred_values = zeros(1, T2-lag);
% 		for j = 1:T2-lag
% 			pred_values(j) = sum(sum(cur_ref_coeffs{i} .* cur_ref_series(:, j:j+lag-1)));
% 		end
% 		resid = cur_ref_series(i, lag+1:T2) - pred_values;
% 		sigma2 = sqrt(resid * resid' / length(resid));
% 		
% 		
% 		mu1 = reshape(ref_coeffs{i}', [], 1)' * mean(cur_PHI)';
% 		mu2 = reshape(cur_ref_coeffs{i}', [], 1)' * mean(cur_PHI)';
		
		sigma2 = sqrt(var(cur_ref_series(i,:)));
		
		ref_anomaly_scores(start) = max(myAnomalyScore(sigma1, sigma2, 0, 0), ...
			myAnomalyScore(sigma2, sigma1, 0, 0));
	end
	%hist(ref_anomaly_scores);
	%disp(ref_anomaly_scores);
	para = expfit(ref_anomaly_scores);
	anomaly_threshs(i) = expinv(alpha, para);
end


%% detect anomaly in test data
disp('testing...');
test_coeffs = cell(p, slide_times+1);
anomaly_scores = zeros(p, slide_times+1);

for off_set = 0 : slide_times
	%disp(['sliding #' num2str(off_set)]);
	
	test_series = time_series(:, test_indices + off_set);

	[temp, X_test] = ...
		ts_lasso_ref_regression(test_series, lag, lambda1, ref_coeffs, lambda2, NC);
	for i = 1:p
		test_coeffs{i, off_set+1}=temp{i};
	end
	

	%compute the anomaly score:
	cur_anomaly_scores = zeros(p,1);
	for i = 1:p
		delta = mean(X_test)';
		coeffs = reshape(ref_coeffs{i}', [], 1);
		mu1 = coeffs' * delta;
		coeffs = reshape(test_coeffs{i,off_set+1}', [], 1);
		mu2 = coeffs' * delta;
		
% 		[~, T1] = size(ref_series);
% 		pred_values = zeros(1, T1-lag);
% 		for j = 1:T1-lag
% 			pred_values(j) = sum(sum(ref_coeffs{i} .* ref_series(:, j:j+lag-1)));
% 		end
% 		resid = ref_series(i, lag+1:T1) - pred_values;
% 		sigma1 = sqrt(resid * resid' / length(resid));
		sigma1 = sqrt(var(ref_series(i, :)));
		
% 		[~, T2] = size(test_series);
% 		pred_values = zeros(1, T2-lag);
% 		for j = 1:T2-lag
% 			pred_values(j) = sum(sum(test_coeffs{i} .* test_series(:, j:j+lag-1)));
% 		end
% 		resid = test_series(i, lag+1:T2) - pred_values;
% 		sigma2 = sqrt(resid * resid' / length(resid));
		sigma2 = sqrt(var(test_series(i, :)));
		
		cur_anomaly_scores(i) = max(myAnomalyScore(sigma1, sigma2, mu1, mu2), ...
			myAnomalyScore(sigma2, sigma1, mu2, mu1));
		anomaly_scores(i, off_set+1) = cur_anomaly_scores(i);
	end
end

end

function [coeffs, PHI] = ts_lasso_regression(series, lag, lambda)
	[p, T] = size(series);
	coeffs = cell(p,1);

	D = p * lag;
	N = T - lag;

	%prepare design matrix
	PHI = zeros(N,D);
	t = zeros(N,1);
	for i = 1:N
		for j = 1:p
			cur_row_start = (j-1)*lag+1;
			cur_row_end = cur_row_start + lag - 1;
			PHI(i, cur_row_start:cur_row_end) = series(j,i:(i+lag-1));
		end
	end

	%do regression with each time series as target
	for target_row = 1:p
		%X_test = normalize(X_test);
		t(1:N, 1) = series(target_row, (lag+1):(lag+N))';
		%y_test = center(y_test);
		
		%[b_opt,~,~] = Lasso2LambdaShooting(X,y,lambda1, lambda2, zero_indices, nonzero_indices);
		%[b_opt,~,~] = myLassoRefShooting(X_test, y_test, lambda1, cur_ref_coeffs, lambda2);
		[b_opt,~,~] = LassoShooting(PHI, t, lambda);
		%b_opt is the optimal coefficients
		coeffs{target_row} = vec2mat(b_opt, lag);
	end
end

function [coeffs, PHI] = ...
	ts_lasso_ref_regression(series, lag, lambda1, ref_coeffs, lambda2, NC)
	[p, T] = size(series);
	coeffs = cell(p,1);

	D = p * lag;
	N = T - lag;

	%prepare design matrix
	PHI = zeros(N,D);
	t = zeros(N,1);
	for i = 1:N
		for j = 1:p
			cur_row_start = (j-1)*lag+1;
			cur_row_end = cur_row_start + lag - 1;
			PHI(i, cur_row_start:cur_row_end) = series(j,i:(i+lag-1));
		end
	end

	%do regression with each time series as target
	for target_row = 1:p
		%X_test = normalize(X_test);
		t(1:N, 1) = series(target_row, (lag+1):(lag+N))';
		%y_test = center(y_test);
		
		cur_ref_coeffs = reshape(ref_coeffs{target_row}', [], 1);
 		
		
		if NC == 1 %neighborhood similarity
			zero_indices = find(cur_ref_coeffs == 0)';
			nonzero_indices = find(cur_ref_coeffs ~= 0)';
			[b_opt,~,~] = Lasso2LambdaShooting(PHI,t,lambda1, lambda2, zero_indices, nonzero_indices);
		else %coefficient similarity
			[b_opt,~,~] = myLassoRefShooting(PHI, t, lambda1, cur_ref_coeffs, lambda2);
		end
		
		%[b_opt,~,~] = myLassoRefShooting(PHI, t, lambda1, cur_ref_coeffs, lambda2);
		%[b_opt,~,~] = LassoShooting(PHI, t, lambda);
		%b_opt is the optimal coefficients

		coeffs{target_row} = vec2mat(b_opt, lag);
	end
end
