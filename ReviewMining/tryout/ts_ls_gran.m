function coeffs = ts_ls_gran(data, train_idx_start, train_idx_end, lag, lambda)

  [coeffs, PHI] = ts_lreg(data(:,train_idx_start:train_idx_end), lag, lambda);
