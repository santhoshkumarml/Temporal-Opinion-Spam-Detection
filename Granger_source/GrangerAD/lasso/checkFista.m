function checkFista
N = 1000;
P = 50;
[X Y C] = generate(N, P);



% V1 = getV(B, X, Y);
% G = getG(B, X, Y);
% 
% h = 0.000001;
% B(1) = B(1)+h;
% V2 = getV(B, X, Y);
% 
% (V2 - V1)/h
% G(1)
% [0 0.1 0.5 1 2 4 10 50 
lambda = [0 0.1 0.5 1 2 4 10 50];
ZL = zeros(size(lambda));
DL = zeros(size(lambda));
EL = zeros(size(lambda));
SL = zeros(size(lambda));
L = zeros(size(lambda));
l = 10000;
V_old = 1000;
for j = 1%:length(lambda)
    
    B = rand(1, P);
    for i = 1:100000
        B = updateB(X, Y, lambda(j), B, l);
        V = getV(B, X, Y);
        if mod(i, 100) == 0
            fprintf('Value = %f\n', V)
        end
        if abs(V_old-V)< 1e-6
            break
        else
            V_old = V;
        end
    end
    
    
    tic;    D = LassoBlockCoordinate(X',Y',lambda(j));  toc
    tic;    E = LassoGaussSeidel(X',Y',lambda(j));      toc
    tic;    S = LassoShooting(X',Y',lambda(j));         toc
    DL(j) = sum(D == 0);
    EL(j) = sum(E == 0);
    SL(j) = sum(S == 0);
    
    ZL(j) = sum(B == 0);
    L(j) = norm(B-C, 2);
    clc
    fprintf('Done Iteration #%d\n', j)
end

plot(lambda, ZL)
hold on
plot([lambda(1), lambda(end)], sum(C == 0)*[1, 1], 'r')

plot(lambda, DL, 'g')
plot(lambda, EL, 'k')
plot(lambda, SL, 'm')

end

function [X Y, B] = generate(N, P)

B = zeros(1, P);
B([1, 20, 22, 31, 43]) = 1;
X = randn(P, N);
Y = B*X + 0.1*randn(1, N);
end

function out = updateB(X, Y, lambda, B, l)
Psi = B - getG(B, X, Y)/l;

out = Psi;
for i = 1:length(B)
    out(i) = argmin(lambda/l, Psi(i));
end

end

function ar = argmin(lal, theta0)
if (theta0 >0) && (abs(theta0) > lal)
    ar = theta0 - lal;
elseif (theta0< 0) && (abs(theta0) > lal)
    ar = theta0 + lal;
else
    ar = 0;
end
end

function G = getG(B, X, Y)
G = B;
for i = 1:length(B)
    G(i) = -2*sum(X(i, :).*(Y-B*X));
end
end

function V = getV(B, X, Y)
V = sum((Y - B*X).^2);
end