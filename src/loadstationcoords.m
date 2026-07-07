% Load station coordinates from table
function [station_x,station_y] = loadstationcoords(station_coords)

coord_names = station_coords.Properties.VariableNames;

if all(ismember({'lon','lat'},coord_names))
    station_x = station_coords.lon;
    station_y = station_coords.lat;
elseif all(ismember({'x','y'},coord_names))
    station_x = station_coords.x;
    station_y = station_coords.y;
elseif all(ismember({'longitude','latitude'},coord_names))
    station_x = station_coords.longitude;
    station_y = station_coords.latitude;
else
    error('Station coordinate file must contain i) lon, lat, ii) x, y, iii) longitude, latitude coordinate variables.')
end

end