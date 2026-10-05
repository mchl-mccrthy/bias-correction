function [bc_grid_clim_var,grid_biases] = mapquantiles(raw_grid_clim_var,...
    station_x,station_y,station_z,qmfs,raw_x,raw_y,raw_z,bc_type,qmf_period,...
    raw_time,idw_power,use_parallel,coordinate_system,idw_alpha)

% Get quantiles
station_quantiles = qmfs.station_quantiles;
raw_quantiles = qmfs.raw_quantiles;

% Get biases
biases = getquantilebiases(station_quantiles,raw_quantiles,bc_type);

% Get size of downscaled raw gridded variable
n_rows = size(raw_grid_clim_var,1);
n_cols = size(raw_grid_clim_var,2);
n_timesteps = size(raw_grid_clim_var,3);

% Preallocate space for downscaled, bias-corrected gridded variable
bc_grid_clim_var = nan(n_rows,n_cols,n_timesteps,class(raw_grid_clim_var));

% Precompute grid-station distances for IDW interpolation
grid_x = raw_x(:);
grid_y = raw_y(:);
grid_z = raw_z(:);
D_all = getdistances(grid_x,grid_y,station_x,station_y,...
    coordinate_system,grid_z,station_z,idw_alpha);

% Precompute nearest grid cell for each station
[station_rows,station_cols] = indexofclosest2( ...
    station_x,station_y,raw_x,raw_y);
station_lin_inds = sub2ind(size(raw_x),station_rows,station_cols);

% Loop through time steps, preserving grid_biases if required
if nargout > 1
    grid_biases = nan(n_rows,n_cols,n_timesteps,class(raw_grid_clim_var));
    if use_parallel
        parfor i_timestep = 1:n_timesteps
            [bc_grid_clim_var(:,:,i_timestep), ...
                grid_biases(:,:,i_timestep)] = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_x,bc_type,idw_power);
        end
    else
        for i_timestep = 1:n_timesteps
            [bc_grid_clim_var(:,:,i_timestep), ...
                grid_biases(:,:,i_timestep)] = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_x,bc_type,idw_power);
        end
    end
else
    if use_parallel
        parfor i_timestep = 1:n_timesteps
            bc_grid_clim_var(:,:,i_timestep) = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_x,bc_type,idw_power);
        end
    else
        for i_timestep = 1:n_timesteps
            bc_grid_clim_var(:,:,i_timestep) = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_x,bc_type,idw_power);
        end
    end
end

end
