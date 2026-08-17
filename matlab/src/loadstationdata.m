% Load station data
function [station_clim_var,station_coords,station_x,station_y,station_z,...
    station_time] = loadstationdata(file_path_station_clim_var,...
    file_path_station_coords)

% Load climate variable at station
station_clim_var = readtable(file_path_station_clim_var,...
    'VariableNamingRule','preserve');

% Load coordinates of stations
station_coords = readtable(file_path_station_coords); 

% Make date variable
station_time = datetime(station_clim_var.year,station_clim_var.month,...
    station_clim_var.day);

% Remove year, month, day fields
station_clim_var.year = [];
station_clim_var.month = [];
station_clim_var.day = [];

% Match coordinates to station columns in the climate variable table
station_coords = matchstationcoords(station_coords,...
    station_clim_var.Properties.VariableNames);
[station_x,station_y,station_z] = loadstationcoords(station_coords);

% Check station coordinates are the same size as climate data
if numel(station_x) ~= width(station_clim_var)
    error('Number of station coordinates must match number of station data columns.')
end

end

% Match station coordinates to the station climate variable columns
function station_coords = matchstationcoords(station_coords,station_names)

coord_names = station_coords.Properties.VariableNames;
if ~any(strcmp(coord_names,'station'))
    error('EQTM:loadstationdata:StationColumnMissing',...
        'Station coordinate file must contain a station column.')
end

coord_station_names = string(station_coords.station);
if numel(unique(coord_station_names)) ~= numel(coord_station_names)
    error('EQTM:loadstationdata:DuplicateStations',...
        'Station coordinate file contains duplicate stations.')
end

station_names = string(station_names);
[is_match,ind_match] = ismember(station_names,coord_station_names);
if any(~is_match)
    missing_names = strjoin(station_names(~is_match),', ');
    error('EQTM:loadstationdata:StationMissing',...
        'Station coordinates missing for: %s',missing_names)
end

station_coords = station_coords(ind_match,:);

end
