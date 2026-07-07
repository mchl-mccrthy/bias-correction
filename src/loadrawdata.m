% Load raw gridded climate data
function [raw_clim_var,grid_x,grid_y,raw_time] = loadrawdata(...
    file_path_raw_data,clim_var_name)

% Load data
raw_clim_var = ncread(file_path_raw_data,clim_var_name);
raw_time = ncread(file_path_raw_data,'time');
[grid_x,grid_y] = loadgridcoords(file_path_raw_data);

% Permute climate variable
raw_clim_var = permute(raw_clim_var,[2 1 3]);

% Process time
raw_time_units = ncreadatt(file_path_raw_data,'time','units');
parts = regexp(raw_time_units, ...
    '^(?<unit>\w+)\s+since\s+(?<ref>.+)$','names','once');
try
    raw_start_time = datetime(strtrim(parts.ref), ...
        'InputFormat','yyyy-MM-dd HH:mm:ss');
catch
    raw_start_time = datetime(strtrim(parts.ref), ...
        'InputFormat','yyyy-MM-dd');
end
switch lower(parts.unit)
    case {'day','days'}
        raw_time = raw_start_time + days(raw_time);
    case {'hour','hours'}
        raw_time = raw_start_time + hours(raw_time);
    case {'second','seconds'}
        raw_time = raw_start_time + seconds(raw_time);
    otherwise
        error('Unsupported time unit: %s',parts.unit)
end

end