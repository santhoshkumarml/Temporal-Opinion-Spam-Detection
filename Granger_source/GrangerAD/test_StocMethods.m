clear all;
close all;
clc;

train_file = 'TE_process/d00.dat';
for j = 1:21
	if j ~= 3
		continue;
	end
	
	disp(j);
	
	if j < 10
		test_file = ['TE_process/d0' num2str(j) '_te.dat'];
	else
		test_file = ['TE_process/d' num2str(j) '_te.dat'];
	end
	series = [load(train_file) load(test_file)'];

	T1 = 500;
	T2 = 960;
	window = 10;
	N = 52;
	%set lag as in Russel & Chiang:
	L = 2;
	if j == 6
		L = 6;
	end
	if (j >= 9 && j <=11) || (j >= 14 && j <= 16) || j == 19 || j == 20
		L = 3;
	end
	
	%% do anomaly detection with a sliding window:
	
	disp('PSGD_Yahoo in progress...');
	tic;
	[Yahoo_ref_coeffs, Yahoo_test_coeffs, Yahoo_anomaly_scores, ...
		Yahoo_threshs] = ...
		granger_stoc_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.99, 1000, 1000, 2);
	figure; plot([Yahoo_anomaly_scores(51,:)' ones(960, 1)*Yahoo_threshs(51)])
	time_Yahoo = toc; %done!
	
	
	disp('Basic stocSubGD in progress...');
	
	tic;
	[stocSubGD_ref_coeffs, stocSubGD_test_coeffs, stocSubGD_anomaly_scores, ...
		stocSubGD_threshs] = ...
		granger_stoc_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.99, 0.01, 0.1, 0);
	figure; plot([stocSubGD_anomaly_scores(51,:)' ones(960, 1)*stocSubGD_threshs(51)])
	time_stocSubGD = toc; %done!
 	
	disp('SCD in progress...');
	tic;
	
	[SCD_ref_coeffs, SCD_test_coeffs, SCD_anomaly_scores, ...
		SCD_threshs] = ...
		granger_stoc_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.99, 1000, 1000, 1);
	figure; plot([SCD_anomaly_scores(51,:)' ones(960, 1)*SCD_threshs(51)])
	time_SCD = toc;
 	
	disp('SGLD in progress...');
	tic;
	[SGLD_ref_coeffs, SGLD_test_coeffs, SGLD_anomaly_scores, ...
		SGLD_threshs] = ...
		granger_stoc_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.99, 1000, 0, 3);
	time_SGLD = toc;%done!
	
	disp('Shotgun in progress...');
	tic;
	[Shotgun_ref_coeffs, Shotgun_test_coeffs, Shotgun_anomaly_scores, ...
		Shotgun_threshs] = ...
		granger_stoc_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.99, 1000, 1000, 4);
	time_Shotgun = toc; %done!
    
 	%% save results
 	save(['TE_process/d0' num2str(j) '_SGD_PSGDResults.mat']);
end



