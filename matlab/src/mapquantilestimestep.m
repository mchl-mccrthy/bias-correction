function [bc_grid_clim_var_timestep,grid_biases_timestep] = ...
    mapquantilestimestep( ...
    raw_grid_clim_var_timestep,station_lin_inds,raw_quantiles,biases, ...
    raw_time_timestep,qmf_period,D_all,grid_x,bc_type,idw_power)

% Interpolate to station locations
n_stations = numel(station_lin_inds);
raw_station_clim_var_timestep = ...
    raw_grid_clim_var_timestep(station_lin_inds);

% Make condition for qmf period
if strcmp(qmf_period,'whole')
    i_period = 1;
elseif strcmp(qmf_period,'seasonal')
    i_period = season(raw_time_timestep);
elseif strcmp(qmf_period,'monthly')
    i_period = month(raw_time_timestep);
end

% Get interpolated biases for those stations. Here it does not matter if
% biases are multiplicative or additive.
station_biases_timestep = nan(1,n_stations);
for i_station = 1:n_stations
    station_biases_timestep(i_station) = interpolatequantilebias(...
        raw_station_clim_var_timestep(i_station),...
        raw_quantiles(:,i_station,i_period),...
        biases(:,i_station,i_period));
end

% Interpolate biases to grid  
valid = isfinite(station_biases_timestep);
D = D_all(:,valid);
b = station_biases_timestep(valid);
W = D.^-idw_power;
W = W./sum(W,2);
grid_biases_timestep = W*b(:);
grid_biases_timestep = reshape(grid_biases_timestep,size(grid_x));

% In case interpolation introduced sub-zero values, which shouldn't
% happen
if strcmp(bc_type,'multiplicative')
    grid_biases_timestep(grid_biases_timestep < 0) = 0;
end

% Apply biases to get downscaled, bias-corrected
% gridded variable for timestep
if strcmp(bc_type,'multiplicative') 
    bc_grid_clim_var_timestep = ...
        grid_biases_timestep.*raw_grid_clim_var_timestep;
elseif strcmp(bc_type,'additive')
    bc_grid_clim_var_timestep = ...
        grid_biases_timestep+raw_grid_clim_var_timestep;
end

end
