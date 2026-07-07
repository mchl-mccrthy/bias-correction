% Load grid coordinates from NetCDF file
function [grid_x,grid_y] = loadgridcoords(file_path_raw_data)

if hasncvar(file_path_raw_data,'lon') && hasncvar(file_path_raw_data,'lat')
    x = ncread(file_path_raw_data,'lon');
    y = ncread(file_path_raw_data,'lat');
elseif hasncvar(file_path_raw_data,'x') && hasncvar(file_path_raw_data,'y')
    x = ncread(file_path_raw_data,'x');
    y = ncread(file_path_raw_data,'y');
elseif hasncvar(file_path_raw_data,'longitude') && hasncvar(file_path_raw_data,'latitude')
    x = ncread(file_path_raw_data,'longitude');
    y = ncread(file_path_raw_data,'latitude');
else
    error('Grid file must contain i) lon, lat, ii) x, y, iii) longitude, latitude coordinate variables.')
end

[grid_x,grid_y] = meshgrid(x,y);

end