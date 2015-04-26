function anomaly_score = myAnomalyScore(sigma1, sigma2, mu1, mu2)
anomaly_score = log(sigma2/sigma1) - ...
	0.5*(1 - 1/(sigma2^2) * (sigma1^2 + (mu1-mu2)^2));
end