function [coeffs] =	lasso_granger(series, lag,lambda, alg, pars)
% returns the coefficients on the reference data and test data, as well as
%		the anomaly scores between reference data and test data
% time_series: each time series forms a row of time_series
% lag: lag time
% lambda: regularization term
% alg: algorithm for regulized regression, choose between 1-6.
%       1. Stochastic Subgradient Descent
%       2. Stochastic Coordinate Descent
%       3. Stochasitc Subgradient Langevin Dynamics
%       4. Parallel Stochastic Coordinate Descent
%       5. Parallel Stochastic Gradient Descent
%       6. Lasso Shooting
% pars: parameter stucture for chosen regulized regression algorithm. See
% details in each .m file.
%       e.g. when alg=1
%       "
%       pars.eta     = 0.0001
%       pars.maxIter = 1000
%       pars.detail  = 0
%       “
%       will call PStocSubGD(X, y, pars.eta,lambda, pars.maxIter, 0, pars.detail)

%% process data

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
    if alg == 1
        [b_opt] = PStocSubGD(PHI, t, pars.eta, lambda, pars.maxIter, 0, pars.detail);
    elseif alg == 2
        [b_opt] = SCD(PHI, t,lambda, pars.method, pars.maxIter, pars.detail);
    elseif alg == 3
        [b_opt] = SGLD(PHI, t, pars.a, pars.b, pars.gama, lambda, pars.batch_size, pars.maxIter, pars.detail);
    elseif alg == 4
        [b_opt] = PStocSubGD(PHI, t, pars.eta, lambda, pars.maxIter, 1, pars.detail);
    elseif alg == 5
        [b_opt] = PSGD_Yahoo(PHI, t, pars.eta, lambda, pars.detail);
    else
        [b_opt,~,~] = LassoShooting(PHI, t, lambda);
    end
    
    %b_opt is the optimal coefficients
    coeffs{target_row} = vec2mat(b_opt, lag);
end

end

