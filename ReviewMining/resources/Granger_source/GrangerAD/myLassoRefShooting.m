function [w,wp,m] = myLassoRefShooting(X, y, lambda1,ref_w,lambda2,varargin)
% This function solves regression with regularization term 
% lambda1 * sigma(|beta_i - ref_w_i|) + lambda2*sigma(|beta_1|);

% y_new = y - X*ref_w;
% [gama, wp, m] = LassoShooting(X, y_new, lambda1);
% w = gama + ref_w;

[maxIter,verbose,optTol,zeroThreshold] = process_options(varargin,'maxIter',1000,'verbose',0,'optTol',1e-5,'zeroThreshold',1e-4);
[n p] = size(X);

% Start from the Least Squares solution
beta = (X'*X + lambda1*eye(p))\(X'*y);
wp = beta;
%beta = (X'*X + lambda*eye(p))\(X'*y); 
% Start the log
if verbose==2
    w_old = beta;
    fprintf('%10s %10s %15s %15s %15s\n','iter','shoots','n(w)','n(step)','f(w)');
    k=1;
    wp = beta;
end

m = 0;

XX2 = X'*X*2;
Xy2 = X'*y*2;
while m < maxIter
        
    beta_old = beta;
    for j = 1:p
        
        % Compute the Shoot and Update the variable
        S0 = sum(XX2(j,:)*beta) - XX2(j,j)*beta(j) - Xy2(j);
		if ref_w(j) >= 0
			slope = XX2(j,j);
			th1 = lambda1+lambda2;
			th2 = lambda1-lambda2;
			th3 = lambda1-lambda2 - slope*ref_w(j);
			th4 = -lambda1-lambda2-slope*ref_w(j);
			
			if S0 > th1
				beta(j,1) = (th1 - S0)/slope;
			elseif S0 <= th1 && S0 >= th2
				beta(j,1) = 0;
			elseif S0 < th2 && S0 > th3
				beta(j,1) = (th2-S0)/slope;
			elseif S0 <= th3 && S0 >= th4
				beta(j,1) = ref_w(j);
			elseif S0 < th4
				beta(j,1) = (-lambda1-lambda2-S0)/slope;
			end
		end
		if ref_w(j) < 0
			slope = XX2(j,j);
			th1 = lambda1+lambda2+slope * abs(ref_w(j));
			th2 = lambda2-lambda1+slope * abs(ref_w(j));
			th3 = lambda2-lambda1;
			th4 = -lambda1-lambda2;
			
			if S0 > th1
				beta(j,1) = (lambda1+lambda2 - S0)/slope;
			elseif S0 <= th1 && S0 >= th2
				beta(j,1) = ref_w(j);
			elseif S0 < th2 && S0 > th3
				beta(j,1) = (th3-S0)/slope;
			elseif S0 <= th3 && S0 >= th4
				beta(j,1) = 0;
			elseif S0 < th4
				beta(j,1) = (th4-S0)/slope;
			end
		end
        
    end
    
    m = m + 1;
    
    % Update the log
    if verbose==2
        fprintf('%10d %10d %15.2e %15.2e %15.2e\n',m,m*p,sum(abs(beta)),sum(abs(beta-w_old)),...
            sum((X*beta-y).^2)+lambda1*sum(abs(beta-ref_w))+ ...
			lambda2*sum(abs(beta)));
        w_old = beta;
        k=k+1;
        wp(:,k) = beta;
    end
    % Check termination
    if sum(abs(beta-beta_old)) < optTol
        break;
    end
    
end
if verbose
    fprintf('Number of iterations: %d\nTotal Shoots: %d\n',m,m*p);
end
w = beta;

end