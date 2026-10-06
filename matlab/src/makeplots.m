% Make diagnostic plots for bias correction
function makeplots(diagnostics,cfg)

% Unpack config
clim_var_name = cfg.clim_var_name;
clim_var_long_name = cfg.clim_var_long_name;
clim_var_units = formatunits(cfg.clim_var_units);
agg_method = cfg.agg_method;
coordinate_system = cfg.coordinate_system;
file_path_figures_tables = cfg.file_path_figures_tables;

% Create figure folder if needed
if ~exist(file_path_figures_tables,'dir')
    mkdir(file_path_figures_tables)
end
file_path_overview = fullfile(file_path_figures_tables,'overview');
file_path_individual_stations = fullfile(file_path_figures_tables,'individual_stations');
if ~exist(file_path_overview,'dir')
    mkdir(file_path_overview)
end
if ~exist(file_path_individual_stations,'dir')
    mkdir(file_path_individual_stations)
end

% Unpack diagnostics
grid_x = diagnostics.grid_x;
grid_y = diagnostics.grid_y;
grid_time = diagnostics.grid_time;
station_clim_var = diagnostics.station_clim_var;
station_coords = diagnostics.station_coords;
station_time = diagnostics.station_time;
raw_station_clim_var = diagnostics.raw_station_clim_var;
bc_station_clim_var = diagnostics.bc_station_clim_var;
station_clim_var_yearly = diagnostics.station_clim_var_yearly;
raw_station_clim_var_yearly = diagnostics.raw_station_clim_var_yearly;
bc_station_clim_var_yearly = diagnostics.bc_station_clim_var_yearly;
years = diagnostics.years;
station_theil_sen_slopes = diagnostics.station_theil_sen_slopes;
raw_station_theil_sen_slopes = diagnostics.raw_station_theil_sen_slopes;
bc_station_theil_sen_slopes = diagnostics.bc_station_theil_sen_slopes;
raw_station_quantile_mae = diagnostics.raw_station_quantile_mae;
bc_station_quantile_mae = diagnostics.bc_station_quantile_mae;
raw_station_annual_mae = diagnostics.raw_station_annual_mae;
bc_station_annual_mae = diagnostics.bc_station_annual_mae;
raw_grid_domain_mean = diagnostics.raw_grid_domain_mean;
bc_grid_domain_mean = diagnostics.bc_grid_domain_mean;
raw_grid_clim_var_yearly = diagnostics.raw_grid_clim_var_yearly;
bc_grid_clim_var_yearly = diagnostics.bc_grid_clim_var_yearly;
bc_grid_theil_sen_slopes = diagnostics.bc_grid_theil_sen_slopes;
station_x = diagnostics.station_x;
station_y = diagnostics.station_y;

% Make maps of long-term average and Theil-Sen slopes
plotmaps(grid_x,grid_y,station_x,station_y,bc_grid_clim_var_yearly,...
    bc_grid_theil_sen_slopes,file_path_overview,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method,coordinate_system);

% Make time series of timestep domain-mean gridded values
plotoverviewtimesteptimeseries(raw_grid_domain_mean,bc_grid_domain_mean,...
    grid_time,file_path_overview,clim_var_name,clim_var_long_name,...
    clim_var_units);

% Make time series of domain-mean annual gridded values
plotoverviewtimeseries(raw_grid_clim_var_yearly,bc_grid_clim_var_yearly,...
    years,file_path_overview,clim_var_name,clim_var_long_name,...
    clim_var_units,agg_method,grid_y,coordinate_system);

% Make scatter plot of Theil-Sen slopes
plottrendcomparison(station_theil_sen_slopes,...
    raw_station_theil_sen_slopes,bc_station_theil_sen_slopes,...
    file_path_overview,clim_var_name,clim_var_long_name,clim_var_units,...
    agg_method);

% Make strip plot of quantile mean absolute errors
plotquantilemae(raw_station_quantile_mae,bc_station_quantile_mae,...
    file_path_overview,clim_var_name,clim_var_long_name,clim_var_units);

% Make strip plot of annual mean absolute errors
plotannualmae(raw_station_annual_mae,bc_station_annual_mae,...
    file_path_overview,clim_var_name,clim_var_long_name,clim_var_units,...
    agg_method);

% Make strip plot of Theil-Sen slope mean absolute errors
plottrendmae(station_theil_sen_slopes,...
    raw_station_theil_sen_slopes,bc_station_theil_sen_slopes,...
    file_path_overview,clim_var_name,clim_var_long_name,clim_var_units,...
    agg_method);

% Make quantile-quantile plots for all stations
plotallstationsqq( ...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,...
    station_time,grid_time,file_path_overview,clim_var_name,...
    clim_var_long_name,clim_var_units);

% Make quantile-mapping residual plots for all stations
plotallstationsqmresiduals( ...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,...
    station_time,grid_time,file_path_overview,clim_var_name,...
    clim_var_long_name,clim_var_units);

% Make plot of station data availability
plotstationavailability( ...
    station_clim_var,station_coords,station_time,...
    file_path_overview,clim_var_name);

% Make diagnostic plots for each station
plotstationdiagnostics( ...
    station_clim_var,station_coords,station_time,...
    raw_station_clim_var,bc_station_clim_var,grid_time,...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years,file_path_individual_stations,...
    clim_var_name,clim_var_long_name,clim_var_units);

end
