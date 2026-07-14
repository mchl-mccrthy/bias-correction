% Load station data
function [station_clim_var,station_coords,station_x,station_y,station_z,...
    station_time] = loadstationdata(file_path_station_clim_var,...
    file_path_station_coords)

% Load climate variable at station
station_clim_var = readtable(file_path_station_clim_var,...
    'VariableNamingRule','preserve');

% Load coordinates of stations
station_coords = readtable(file_path_station_coords); 
[station_x,station_y,station_z] = loadstationcoords(station_coords);

% Make date variable
station_time = datetime(station_clim_var.year,station_clim_var.month,...
    station_clim_var.day);

% Remove year, month, day fields
station_clim_var.year = [];
station_clim_var.month = [];
station_clim_var.day = [];

% Check station coordinates are the same size as climate data
if numel(station_x) ~= width(station_clim_var)
    error('Number of station coordinates must match number of station data columns.')
end

end