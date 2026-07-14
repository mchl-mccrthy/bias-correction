% Make diagnostics
function diagnostics = makediagnostics(cfg)

% Unpack workflow configuration
clim_var_name = cfg.clim_var_name;
agg_method = cfg.agg_method;
file_path_station_coords = cfg.file_path_station_coords;
file_path_station_clim_var = cfg.file_path_station_clim_var;
file_path_raw_data = cfg.file_path_raw_data;
file_path_bc_data = cfg.file_path_bc_data;

% Check if bias-corrected data exist
if ~isfile(file_path_bc_data)
    error('Bias-corrected data file not found: %s',file_path_bc_data)
end

% Load raw data
[raw_grid_clim_var,grid_x,grid_y,~,grid_time] = loadgriddata( ...
    file_path_raw_data,clim_var_name);

% Load bias corrected data
[bc_grid_clim_var,~,~,~,~] = loadgriddata( ...
    file_path_bc_data,clim_var_name);

% Load station data
[station_clim_var,station_coords,station_x,station_y,~,station_time] = ...
    loadstationdata(file_path_station_clim_var,file_path_station_coords);

% Get raw and bias-corrected climate variables at stations
raw_station_clim_var...
    = gridtostations(...
    raw_grid_clim_var,station_x,station_y,grid_x,grid_y,station_clim_var);
bc_station_clim_var...
    = gridtostations(...
    bc_grid_clim_var,station_x,station_y,grid_x,grid_y,station_clim_var);

% Make yearly versions of climate variables at stations
[station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years]...
    = makeyearlytables(...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,grid_time,...
    agg_method);

% Get linear trends at stations
[station_linear_trends,raw_station_linear_trends,bc_station_linear_trends]...
    = getlineartrends(...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years);

% Make a yearly version of the gridded bias-corrected data
[bc_grid_clim_var_yearly,grid_years] = makeyearlygrid( ...
    bc_grid_clim_var,grid_time,agg_method);

% Get linear trends of gridded bias-corrected data
bc_grid_linear_trends = getgridlineartrends( ...
    bc_grid_clim_var_yearly,grid_years);

% Make struct of diagnostics
diagnostics.station_clim_var = station_clim_var;
diagnostics.station_coords = station_coords;
diagnostics.station_x = station_x;
diagnostics.station_y = station_y;
diagnostics.station_time = station_time;
diagnostics.raw_station_clim_var = raw_station_clim_var;
diagnostics.bc_station_clim_var = bc_station_clim_var;
diagnostics.station_clim_var_yearly = station_clim_var_yearly;
diagnostics.raw_station_clim_var_yearly = raw_station_clim_var_yearly;
diagnostics.bc_station_clim_var_yearly = bc_station_clim_var_yearly;
diagnostics.years = years;
diagnostics.station_linear_trends = station_linear_trends;
diagnostics.raw_station_linear_trends = raw_station_linear_trends;
diagnostics.bc_station_linear_trends = bc_station_linear_trends;
diagnostics.bc_grid_clim_var_yearly = bc_grid_clim_var_yearly;
diagnostics.bc_grid_linear_trends = bc_grid_linear_trends;
diagnostics.grid_x = grid_x;
diagnostics.grid_y = grid_y;
diagnostics.grid_time = grid_time;

end