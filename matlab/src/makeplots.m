% Make diagnostic plots for bias correction
function makeplots(diagnostics,cfg)

% Unpack config
clim_var_name = cfg.clim_var_name;
clim_var_long_name = cfg.clim_var_long_name;
clim_var_units = cfg.clim_var_units;
agg_method = cfg.agg_method;
file_path_figures = cfg.file_path_figures;

% Create figure folder if needed
if ~exist(file_path_figures,'dir')
    mkdir(file_path_figures)
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
station_linear_trends = diagnostics.station_linear_trends;
raw_station_linear_trends = diagnostics.raw_station_linear_trends;
bc_station_linear_trends = diagnostics.bc_station_linear_trends;
bc_grid_clim_var_yearly = diagnostics.bc_grid_clim_var_yearly;
bc_grid_linear_trends = diagnostics.bc_grid_linear_trends;
station_x = diagnostics.station_x;
station_y = diagnostics.station_y;

% Make maps of long-term average and linear trends
plotmaps(grid_x,grid_y,station_x,station_y,bc_grid_clim_var_yearly,...
    bc_grid_linear_trends,file_path_figures,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method);

% Make scatter plot of linear trends
plottrendcomparison(station_linear_trends,...
    raw_station_linear_trends,bc_station_linear_trends,...
    file_path_figures,clim_var_name,clim_var_long_name,clim_var_units,...
    agg_method);

% Make quantile-quantile plots for all stations
plotallstationsqq( ...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,...
    station_time,grid_time,file_path_figures,clim_var_name,...
    clim_var_long_name,clim_var_units);

% Make plot of station data availability
plotstationavailability( ...
    station_clim_var,station_coords,station_time,...
    file_path_figures,clim_var_name);

% Make diagnostic plots for each station
plotstationdiagnostics( ...
    station_clim_var,station_coords,station_time,...
    raw_station_clim_var,bc_station_clim_var,grid_time,...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years,file_path_figures,...
    clim_var_name,clim_var_long_name,clim_var_units);

end
