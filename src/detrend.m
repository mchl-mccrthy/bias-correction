function clim_data_detrended = detrend(clim_data, trends, bc_type, eps_val)

if nargin < 4
    eps_val = 0.1; % precipitation threshold/unit-dependent
end

if strcmp(bc_type,'additive')
    clim_data_detrended = clim_data - trends;
else
    clim_data_detrended = (clim_data + eps_val) ./ (trends + eps_val);
end

end