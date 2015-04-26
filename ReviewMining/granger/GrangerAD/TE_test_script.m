%pkg load communications
%pkg load optim
%pkg load statistics

clear all;
close all;
clc;

train_file = 'TE_process/d00.dat';
for j = 1:21
	if j ~= 3 %&& j ~= 9 && j ~= 15
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
	disp('Granger -N AD in progress...');
	tic;
	[granger_ref_coeffs_N, granger_test_coeffs_N, granger_anomaly_scores_N, ...
		granger_threshs_N] = ...
		granger_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.95, 1000, 2000, 800, 1);
	time_granger_N = toc;

	disp('Granger -C AD in progress...');
	tic;
	[granger_ref_coeffs_C, granger_test_coeffs_C, granger_anomaly_scores_C, ...
		granger_threshs_C] = ...
		granger_anomaly_detection(series, L, 1:T1, T1+1-window+1:T1+1, T2-1, ...
		0.95, 1000, 1000, 10, 2);
	time_granger_C = toc;
 	
 	save(['TE_process/d0' num2str(j) '_totResults.mat']);
end



