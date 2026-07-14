% Load grid coordinates from NetCDF file
function [grid_x,grid_y,grid_z] = loadgridcoords(file_path_grid_data)

if hasncvar(file_path_grid_data,'lon') && hasncvar(file_path_grid_data,'lat')
    x = ncread(file_path_grid_data,'lon');
    y = ncread(file_path_grid_data,'lat');
elseif hasncvar(file_path_grid_data,'x') && hasncvar(file_path_grid_data,'y')
    x = ncread(file_path_grid_data,'x');
    y = ncread(file_path_grid_data,'y');
elseif hasncvar(file_path_grid_data,'longitude') && hasncvar(file_path_grid_data,'latitude')
    x = ncread(file_path_grid_data,'longitude');
    y = ncread(file_path_grid_data,'latitude');
else
    error('Grid file must contain i) lon, lat, ii) x, y, iii) longitude, latitude coordinate variables.')
end

[grid_x,grid_y] = meshgrid(x,y);

if hasncvar(file_path_grid_data,'z')
    grid_z = ncread(file_path_grid_data,'z');
elseif hasncvar(file_path_grid_data,'elevation')
    grid_z = ncread(file_path_grid_data,'elevation');
elseif hasncvar(file_path_grid_data,'elev')
    grid_z = ncread(file_path_grid_data,'elev');
elseif hasncvar(file_path_grid_data,'orog')
    grid_z = ncread(file_path_grid_data,'orog');
else
    grid_z = [];
end

if ~isempty(grid_z)
    grid_z = permute(grid_z,[2 1]);
end

end