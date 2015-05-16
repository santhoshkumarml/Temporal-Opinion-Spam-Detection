function coeffs = sample_test_fn(data, train_idx_start, train_idx_end)
	% no_of_series =5
	% train_data1 = normrnd(0.7,0.1,[no_of_series 82]);
	% val = 4;
	% for i= 1:5
	%     for j= 1:82
	%         if mod(j,20) == 0
	%             train_data1(i,j) = 2;
	%         end
	%     end
	% end

	% train_size = 23

	train_size = train_idx_end-train_idx_start+1

	lambda_start = 10
	lambda_end = 10
	no_of_lambdas = lambda_end-lambda_start+1
	lag_start = 2
	lag_end = 2
	no_of_lags = lag_end-lag_start+1



	% coeffsvec = zeros(no_of_lambdas, no_of_series, 5);
	% PHIvec = zeros(no_of_lambdas, 22, 5);	

	for lambda = lambda_start:lambda_end
	   for lag = lag_start:lag_end
	      [coeffs, PHI] = ts_lreg(data(:,1:train_size), lag, lambda);
	      % coeffsmat = reshape(cell2mat(coeffs),[6,2,6]);
	       %celldisp(coeffs)
	       %coeffsvec(lambda,:,:) = coeffsmat;
	       %PHIvec(lambda,:,:) = PHI;
	    end
	end