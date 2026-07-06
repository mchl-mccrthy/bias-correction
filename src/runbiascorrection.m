% Run bias correction workflow
function results = runbiascorrection(cfg)

%% Display progress
disp('Bias correcting climate data')

%% Validate workflow configuration 
validateconfig(cfg)

%% Get configuration from config file
clim_var_name = cfg.clim_var_name;
clim_var_long_name = cfg.clim_var_long_name;
clim_var_units = cfg.clim_var_units;
qmf_period = cfg.qmf_period;
bc_type = cfg.bc_type;
preserve_trends = cfg.preserve_trends;
trend_window = cfg.trend_window;
agg_method = cfg.agg_method;
write_output = cfg.write_output;
make_plots = cfg.make_plots;
n_quantiles = cfg.n_quantiles;
idw_power = cfg.idw_power;
use_parallel = cfg.use_parallel;
n_workers = cfg.n_workers;
multiplicative_epsilon = cfg.multiplicative_epsilon;
file_path_station_coords = cfg.file_path_station_coords;
file_path_station_clim_var = cfg.file_path_station_clim_var;
file_path_raw_data = cfg.file_path_raw_data;
file_path_bc_data = cfg.file_path_bc_data;
file_path_figures = cfg.file_path_figures;

%% Start parallel pool if requested
if use_parallel && isempty(gcp('nocreate'))
    if isempty(n_workers)
        parpool;
    else
        parpool(n_workers);
    end
end

%% Load climate variable at station and coordinates
[station_clim_var,station_coords,station_lat,station_lon,station_time]...
    = loadstationdata(...
    file_path_station_clim_var,file_path_station_coords);

%% Load raw climate data
[raw_grid_clim_var,raw_lon,raw_lat,raw_time]...
    = loadrawdata(...
    file_path_raw_data,clim_var_name);

%% Get trends in raw and station data
if preserve_trends
    raw_grid_trends...
        = gettrends(...
        raw_grid_clim_var,3,trend_window);
    station_trends...
        = gettrends(...
        station_clim_var{:,:},1,trend_window);
end

%% Detrend raw and station data
if preserve_trends
    raw_grid_clim_var...
        = detrendclimdata(...
        raw_grid_clim_var,raw_grid_trends,bc_type,multiplicative_epsilon);
    station_clim_var{:,:}...
        = detrendclimdata(...
        station_clim_var{:,:},station_trends,bc_type,multiplicative_epsilon);
end

%% Get quantile mapping functions
qmfs...
    = getqmfs(...
    station_clim_var,station_coords,station_time,raw_grid_clim_var,raw_lon,...
    raw_lat,raw_time,qmf_period,n_quantiles);

%% Correct raw data to make bias corrected data
bc_grid_clim_var...
    = mapquantiles(...
    raw_grid_clim_var,station_lon,station_lat,qmfs,raw_lon,raw_lat,...
    bc_type,qmf_period,raw_time,idw_power,use_parallel);

%% Interpolate station trends to grid
if preserve_trends  
    station_grid_trends...
        = interptrends(...
        station_trends,station_coords.lon,station_coords.lat,raw_lon,...
        raw_lat,raw_grid_trends,bc_type,idw_power);
end

%% Clear raw data to avoid OOM
clear raw_grid_clim_var raw_grid_trends

%% Retrend bias corrected data
if preserve_trends
    bc_grid_clim_var...
        = retrendclimdata(...
        bc_grid_clim_var,station_grid_trends,bc_type,multiplicative_epsilon);
end

%% Clear station grid trends to avoid OOM
clear station_grid_trends

%% Reload raw and station data
[raw_grid_clim_var,~,~,~]...
    = loadrawdata(...
    file_path_raw_data,clim_var_name);
[station_clim_var,station_coords,station_lat,station_lon,station_time]...
    = loadstationdata(...
    file_path_station_clim_var,file_path_station_coords);

%% Get raw and bias-corrected climate variables at stations
raw_station_clim_var...
    = gridtostations(...
    raw_grid_clim_var,station_lon,station_lat,raw_lon,raw_lat,...
    station_clim_var);
bc_station_clim_var...
    = gridtostations(...
    bc_grid_clim_var,station_lon,station_lat,raw_lon,raw_lat,station_clim_var);

%% Make yearly versions of station tables
[station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years]...
    = makeyearlytables(...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,raw_time,...
    agg_method);

%% Get linear trends at stations
[station_linear_trends,raw_station_linear_trends,bc_station_linear_trends]...
    = getlineartrends(...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years);

%% Make a yearly version of the bias corrected data
[bc_grid_clim_var_yearly,grid_years] = makeyearlygrid( ...
    bc_grid_clim_var,raw_time,agg_method);

%% Get linear trends of gridded bias corrected data
bc_grid_linear_trends = getgridlineartrends( ...
    bc_grid_clim_var_yearly,grid_years);

%% Make plots
if make_plots 
    makeplots(...
        station_clim_var,station_coords,station_time,raw_station_clim_var,...
        bc_station_clim_var,raw_time,station_clim_var_yearly,...
        raw_station_clim_var_yearly,bc_station_clim_var_yearly,years,...
        station_linear_trends,raw_station_linear_trends,bc_station_linear_trends,raw_lon,raw_lat,...
        file_path_figures,clim_var_name,clim_var_long_name,clim_var_units,...
        bc_grid_clim_var_yearly,bc_grid_linear_trends,agg_method);
end

%% Put bias corrected data in netcdf file
if write_output
    savebcdata(...
        bc_grid_clim_var,file_path_raw_data,file_path_bc_data,clim_var_name)
end

%% Return useful outputs
results.write_output = cfg.write_output;
results.make_plots = cfg.make_plots;
results.file_path_bc_data = file_path_bc_data;
results.mean_bc = nanmean(bc_grid_clim_var,'all');
results.mean_raw = nanmean(raw_grid_clim_var,'all');
results.mean_station = nanmean(table2array(station_clim_var),'all');
results.station_linear_trends = station_linear_trends;
results.raw_station_linear_trends = raw_station_linear_trends;
results.bc_station_linear_trends = bc_station_linear_trends;
results.bc_grid_linear_trends = bc_grid_linear_trends;

%% Display progress
disp('Bias correction completed')

end