function [total_loss] = log_loss(predicted_vals, real_val, lag)
	[no_of_series, series_length] = size(predicted_vals)
	total_loss = 0
	for i = 1:no_of_series
		for j = 1:series_length
			diffsq = (real_val - predicted_val)**2
			loss = -log(exp(-0.5*diffsq)/sqrt(2*pi))
			total_loss += loss
		end
	end
	% mu = zeros(lag);
	% sigma = eye(lag);
	% XW = real_val - predicted_val
	% %XWTSXW = transpose(XW)*sigma*XW
	% cond_prob = exp(-1*XWTSXW)*1/realpow((2*pi),lag/2)
	% return -log(cond_prob)
	%Z = mvnpdf (XY, mu, sigma);