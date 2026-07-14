% Load gridded climate data
function [grid_clim_var,grid_x,grid_y,grid_z,grid_time] = loadgriddata(...
    file_path_grid_data,clim_var_name)

% Load data
grid_clim_var = ncread(file_path_grid_data,clim_var_name);
grid_time = ncread(file_path_grid_data,'time');
[grid_x,grid_y,grid_z] = loadgridcoords(file_path_grid_data);

% Permute climate variable
grid_clim_var = permute(grid_clim_var,[2 1 3]);

% Process time
grid_time_units = ncreadatt(file_path_grid_data,'time','units');
parts = regexp(grid_time_units, ...
    '^(?<unit>\w+)\s+since\s+(?<ref>.+)$','names','once');
if isempty(parts)
    error('Unsupported NetCDF time units format: %s',grid_time_units)
end
try
    grid_start_time = datetime(strtrim(parts.ref), ...
        'InputFormat','yyyy-MM-dd HH:mm:ss');
catch
    grid_start_time = datetime(strtrim(parts.ref), ...
        'InputFormat','yyyy-MM-dd');
end
switch lower(parts.unit)
    case {'day','days'}
        grid_time = grid_start_time + days(grid_time);
    case {'hour','hours'}
        grid_time = grid_start_time + hours(grid_time);
    case {'second','seconds'}
        grid_time = grid_start_time + seconds(grid_time);
    otherwise
        error('Unsupported time unit: %s',parts.unit)
end

end