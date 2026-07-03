% Detrend climate data
function clim_data_detrended = detrendclimdata(clim_data,trends,bc_type,eps_val)

% Set default eps value for multiplicative variables
if nargin < 4
    eps_val = 0.1;
end

% Remove trends
if strcmp(bc_type,'additive')
    clim_data_detrended = clim_data-trends;
else
    clim_data_detrended = (clim_data+eps_val)./(trends+eps_val);
end

end