function [bc_grid_clim_var,grid_biases] = mapquantiles(raw_grid_clim_var,...
    station_lon,station_lat,qmfs,raw_lon,raw_lat,bc_type,qmf_period,...
    raw_time,idw_power,use_parallel,coordinate_system)

% Get quantiles
station_quantiles = qmfs.station_quantiles;
raw_quantiles = qmfs.raw_quantiles;

% Get biases
if strcmp(bc_type,'multiplicative')

    % Wrt precipitation, inf occurs if observation is more than zero and
    % raw gridded is zero, which rarely happens in reality (e.g. McCarthy 
    % et al (2022) Supplementary Information, Figure S4). NaN occurs when 
    % both observation and raw gridded are zero, in which case multiplying
    % the raw gridded by zero is appropriate.  
    biases = station_quantiles./raw_quantiles;
    biases(isnan(biases) | isinf(biases)) = 0;
elseif strcmp(bc_type,'additive')
    biases = station_quantiles-raw_quantiles;
end

% Get size of downscaled raw gridded variable
n_rows = size(raw_grid_clim_var,1);
n_cols = size(raw_grid_clim_var,2);
n_timesteps = size(raw_grid_clim_var,3);

% Preallocate space for downscaled, bias-corrected gridded variable
bc_grid_clim_var = nan(n_rows,n_cols,n_timesteps,class(raw_grid_clim_var));

% Precompute grid-station distances for IDW interpolation
grid_x = raw_lon(:);
grid_y = raw_lat(:);
D_all = getdistances(grid_x,grid_y,station_lon,station_lat,coordinate_system);

% Precompute nearest grid cell for each station
[station_rows,station_cols] = indexofclosest2( ...
    station_lon,station_lat,raw_lon,raw_lat);
station_lin_inds = sub2ind(size(raw_lon),station_rows,station_cols);

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
                D_all,raw_lon,bc_type,idw_power);
        end
    else
        for i_timestep = 1:n_timesteps
            [bc_grid_clim_var(:,:,i_timestep), ...
                grid_biases(:,:,i_timestep)] = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_lon,bc_type,idw_power);
        end
    end

else
    if use_parallel
        parfor i_timestep = 1:n_timesteps
            bc_grid_clim_var(:,:,i_timestep) = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_lon,bc_type,idw_power);
        end
    else
        for i_timestep = 1:n_timesteps
            bc_grid_clim_var(:,:,i_timestep) = ...
                mapquantilestimestep( ...
                raw_grid_clim_var(:,:,i_timestep),station_lin_inds, ...
                raw_quantiles,biases,raw_time(i_timestep),qmf_period, ...
                D_all,raw_lon,bc_type,idw_power);
        end
    end
end

end