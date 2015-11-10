function [coeffs, PHI] = ts_lreg(series, lag, lambda)
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
		t(1:N, 1) = series(target_row, (lag+1):(lag+N))';
		[b_opt,~,~] = LassoShooting(PHI, t, lambda);
		%b_opt is the optimal coefficients
		coeffs{target_row} = vec2mat(b_opt, lag);
	end
end