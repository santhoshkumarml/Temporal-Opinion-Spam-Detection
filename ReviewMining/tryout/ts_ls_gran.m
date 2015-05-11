function coeffs = ts_ls_gran(data, train_idx_start, train_idx_end)

	train_size = train_idx_end-train_idx_start+1

	lambda_start = 10
	lambda_end = 10
	no_of_lambdas = lambda_end-lambda_start+1
	lag_start = 2
	lag_end = 2
	no_of_lags = lag_end-lag_start+1

	for lambda = lambda_start:lambda_end
	   for lag = lag_start:lag_end
	      [coeffs, PHI] = ts_lreg(data(:,1:train_size), lag, lambda);
	    end
	end
end