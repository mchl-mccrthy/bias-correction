% Bias correct gridded climate data
function results = biascorrect(cfg)

% Display progress
disp('Bias correcting climate data')

% Validate workflow configuration 
validateconfig(cfg)

% Unpack config
clim_var_name = cfg.clim_var_name;
qmf_period = cfg.qmf_period;
bc_type = cfg.bc_type;
trend_method = char(cfg.trend_method);
trend_window = cfg.trend_window;
write_output = cfg.write_output;
n_quantiles = cfg.n_quantiles;
idw_power = cfg.idw_power;
idw_method = cfg.idw_method;
idw_alpha = cfg.idw_alpha;
use_parallel = cfg.use_parallel;
n_workers = cfg.n_workers;
multiplicative_epsilon = cfg.multiplicative_epsilon;
keep_grid_biases = cfg.keep_grid_biases;
coordinate_system = cfg.coordinate_system;
file_path_station_coords = cfg.file_path_station_coords;
file_path_station_clim_var = cfg.file_path_station_clim_var;
file_path_raw_data = cfg.file_path_raw_data;
file_path_bc_data = cfg.file_path_bc_data;

% Start parallel pool if requested
if use_parallel && isempty(gcp('nocreate'))
    if isempty(n_workers)
        parpool;
    else
        parpool(n_workers);
    end
end

% Load climate variable at station and coordinates
[station_clim_var,~,station_x,station_y,station_z,station_time] ...
    = loadstationdata(...
    file_path_station_clim_var,file_path_station_coords);

% Load raw climate data
[raw_grid_clim_var,grid_x,grid_y,grid_z,raw_time]...
    = loadgriddata(...
    file_path_raw_data,clim_var_name);

% Get trends in raw and station data
if any(strcmp(trend_method,{'grid','station'}))
    raw_grid_trends...
        = gettrends(...
        raw_grid_clim_var,3,trend_window);
    station_trends...
        = gettrends(...
        station_clim_var{:,:},1,trend_window);
end

% Detrend raw and station data
if any(strcmp(trend_method,{'grid','station'}))
    raw_grid_clim_var...
        = detrendclimdata(...
        raw_grid_clim_var,raw_grid_trends,bc_type,multiplicative_epsilon);
    station_clim_var{:,:}...
        = detrendclimdata(...
        station_clim_var{:,:},station_trends,bc_type,multiplicative_epsilon);
    if strcmp(trend_method,'grid')
        clear station_trends
    end
end

% Get quantile mapping functions
qmfs...
    = getqmfs( ...
    station_clim_var,station_x,station_y,station_time,raw_grid_clim_var,grid_x, ...
    grid_y,raw_time,qmf_period,n_quantiles);

% Correct raw data to make bias corrected data
if keep_grid_biases
    [bc_grid_clim_var,grid_biases]...
        = mapquantiles(...
        raw_grid_clim_var,station_x,station_y,station_z,qmfs,grid_x,grid_y,grid_z,...
        bc_type,qmf_period,raw_time,idw_power,use_parallel,...
        coordinate_system,idw_method,idw_alpha);
else
    bc_grid_clim_var...
        = mapquantiles(...
        raw_grid_clim_var,station_x,station_y,station_z,qmfs,grid_x,grid_y,grid_z,...
        bc_type,qmf_period,raw_time,idw_power,use_parallel,...
        coordinate_system,idw_method,idw_alpha);
end

% Interpolate station trends to grid
if strcmp(trend_method,'station')  
    station_grid_trends...
        = interptrends(...
        station_trends,station_x,station_y,station_z,grid_x,grid_y,grid_z,...
        raw_grid_trends,bc_type,idw_power,coordinate_system,idw_method,...
        idw_alpha);
end

% Clear raw climate data to save memory
clear raw_grid_clim_var

% Retrend bias corrected data
if strcmp(trend_method,'grid')
    bc_grid_clim_var...
        = retrendclimdata(...
        bc_grid_clim_var,raw_grid_trends,bc_type,multiplicative_epsilon);
elseif strcmp(trend_method,'station')
    bc_grid_clim_var...
        = retrendclimdata(...
        bc_grid_clim_var,station_grid_trends,bc_type,multiplicative_epsilon);
end

% Clear raw trends to save memory
clear raw_grid_trends

% Clear station grid trends to save memory
clear station_grid_trends

% Put bias corrected data in netcdf file
if write_output
    savebcdata(...
        bc_grid_clim_var,file_path_raw_data,file_path_bc_data,clim_var_name)
end

% Return useful outputs
results.write_output = cfg.write_output;
results.file_path_bc_data = file_path_bc_data;
results.mean_bc_grid_clim_var = nanmean(bc_grid_clim_var,'all');
if keep_grid_biases
    results.grid_biases = grid_biases;
end

% Display progress
disp('Bias correction completed')

end
