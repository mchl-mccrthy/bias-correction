function [station_clim_var,station_coords,station_lat,...
    station_lon,station_time,n_stations] = loadstationdata(...
    file_path_station_clim_var,file_path_station_coords)

% Load climate variable at station
station_clim_var = readtable(file_path_station_clim_var,...
    'VariableNamingRule','preserve');

% Load coordinates of stations
station_coords = readtable(file_path_station_coords); 
station_lon = station_coords.lon;
station_lat = station_coords.lat;

% Make date variable
station_time = datetime(station_clim_var.year,station_clim_var.month,...
    station_clim_var.day);

% Remove year, month, day fields
station_clim_var.year = [];
station_clim_var.month = [];
station_clim_var.day = [];

% Get number of stations
n_stations = height(station_coords);

end