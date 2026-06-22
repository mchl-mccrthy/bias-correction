function clim_data_retrended = retrend(clim_data, trends, bc_type, eps_val)

if nargin < 4 || isempty(eps_val)
    eps_val = 0.1;
end

if strcmp(bc_type,'additive')
    clim_data_retrended = clim_data + trends;
else
    clim_data_retrended = clim_data .* (trends + eps_val) - eps_val;

    % Prevent negative precipitation, but preserve NaNs
    valid = ~isnan(clim_data_retrended);
    clim_data_retrended(valid) = max(clim_data_retrended(valid), 0);
end

end