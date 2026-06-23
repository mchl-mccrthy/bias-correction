function [raw_clim_var,raw_lon,raw_lat,raw_time] = loadrawdata(file_path_raw_data,clim_var_name)

% Load data
raw_clim_var = ncread(file_path_raw_data,clim_var_name);
raw_clim_var = single(raw_clim_var);
raw_lat = ncread(file_path_raw_data,'lat');
raw_lon = ncread(file_path_raw_data,'lon');
raw_time = ncread(file_path_raw_data,'time');

% Permute climate variable, lat and lon
raw_clim_var = permute(raw_clim_var,[2 1 3]);
[raw_lon,raw_lat] = meshgrid(raw_lon,raw_lat);

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