train_file = 'TE_process/d00.dat';
series = load(train_file);

%set lag as in Russel & Chiang:
L = 2;
lambda = 1;

% %% 1. Stochastic Subgradient Descent
tic;
clear pars
pars.eta     = 0.00000001;
pars.maxIter = 1000;
pars.detail  = 0;
[coeffs1] =	lasso_granger(series, L,lambda, 1, pars);
toc


%% 2. Stochastic Coordinate Descent
tic;
clear pars
pars.maxIter = 1000;
pars.detail  = 0;
pars.method  = 2;
[coeffs2] =	lasso_granger(series, L,lambda, 2, pars);
toc

%% 3. Stochasitc Subgradient Langevin Dynamics
tic;
clear pars
pars.a     = 0.001;
pars.b     = 100;
pars.gama     = -4;
pars.batch_size = 10;
pars.maxIter = 1000;
pars.detail  = 0;
[coeffs3] =	lasso_granger(series, L,lambda, 3, pars);
toc

%% 4. Parallel Stochastic Coordinate Descent
tic;
clear pars
pars.eta     = 0.00000001;
pars.maxIter = 1000;
pars.detail  = 0;
[coeffs4] =	lasso_granger(series, L,lambda, 4, pars);
toc

%% 5. Parallel Stochastic Gradient Descent
tic;
clear pars
pars.eta     = 0.00000001;
pars.detail  = 0;
[coeffs5] =	lasso_granger(series, L,lambda, 5, pars);
toc
% 
% %% 6. Lasso Shooting
% tic;
% clear pars
% pars = 0;
% [coeffs6] =	lasso_granger(series, L,lambda, 6, pars);
% toc
