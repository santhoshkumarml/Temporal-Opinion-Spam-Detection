prepare_housing;

[~, tot_w tot_obj] = SGLangDyn(X, y, 5, 5, 0.001, 1, 0.55);
plot(tot_obj);

[ws, ~, ~] = LassoShooting(X, y, 5);
obj = (X*ws - y)' * (X*ws - y) + 5 * sum(abs(ws));