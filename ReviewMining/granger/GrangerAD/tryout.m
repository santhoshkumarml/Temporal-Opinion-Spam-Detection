clear all;
close all;
clc;

train_data1 = normrnd(0.7,0.4,[4 82]);
for i= 1:4
    for j= 1:82
        if mod(j,20) == 0
            if i~= 1 && i~=3
                train_data1(i,j) = 2;
            else
                train_data1(i,j) = -2;
            end
            train_data1(i,j) = 2;
        end
    end
end



[granger_ref_coeffs_N, granger_test_coeffs_N, granger_anomaly_scores_N, ...
		granger_threshs_N] = ...
		granger_anomaly_detection(train_data1, 1, 1:3,4:6, 76, ...
		0.95, 40, 40, 10, 1);
scores = zeros(4,82);
x = 1:82;
%     plotyy(1:79, data(1:79), 'b', 1:80, scores(i,1:79), 'r');
%     disp(size(scores(i,:)))
%     disp(size(data))
%     disp(size(x))

for i = 1:4
    scores(i,6:82) = granger_anomaly_scores_N(i,:);
    data = train_data1(i,:);
    subplot(4,1,i);
    plotyy(x, data, x, scores(i,:));
end