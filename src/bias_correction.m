% Bias correct climate data

% Notes
% - Raw climate data need to be stored in a particular way. The dimensions
%   of the climate variable must be: lon, lat, time. This is the standard
%   used by ECMWF.
% - Note that this assumes station data are in same time zone as gridded
%   climate data.
% - Station data should also cover the same time period as the gridded
%   data, without any missing days. NaNs are allowed though.

%% Initiate workflow

% Display progress
disp('Bias correcting climate data')

% Specify some variables
clim_var_name = 'tas';
clim_var_long_name = 'Temperature';
clim_var_units = 'C';
qmf_period = 'monthly'; % 'whole','seasonal', or 'monthly'
bias_interp_method = 'idw'; 
bc_type = 'additive';
preserve_trends = 'yes'; % Preserve station trends?
trend_window = 365*5; % days
agg_method = 'mean'; % For yearly aggregations, 'sum' or 'mean'

% Specify file paths
file_path_station_coords = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\stations\StLucia_coordinates.csv';
file_path_station_clim_var = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\stations\StLucia_tas.csv';
file_path_raw_data = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\chelsa\tas_StLucia_1981_2020.nc';
file_path_bc_data = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\processed\key_variables\reanalysis\tas_bc_StLucia_1981_2020.nc';
file_path_figures = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\temp\';

% Add paths 
addpath(genpath('src'))

%% Load climate variable at station and coordinates
[station_clim_var,station_coords,station_lat,station_lon,station_time]...
    = loadstationdata(file_path_station_clim_var,...
    file_path_station_coords);

%% Load raw climate data and format
[raw_clim_var,raw_lon,raw_lat,raw_time] = loadrawdata(file_path_raw_data,...
    clim_var_name);

%% Get trends
if strcmp(preserve_trends,'yes')
    grid_trends = get_trends(raw_clim_var,3,trend_window);
    station_trends = get_trends(station_clim_var{:,:},1,trend_window);
end

%% Detrend
if strcmp(preserve_trends,'yes')
    raw_clim_var = detrend(raw_clim_var,grid_trends,bc_type);
    station_clim_var{:,:} = detrend(station_clim_var{:,:},station_trends,...
        bc_type);
end

%% Get quantile mapping functions
qmfs = get_qmfs(station_clim_var,station_coords,station_time,...
    raw_clim_var,raw_lon,raw_lat,raw_time,qmf_period);

%% Correct reanalysis
bc_clim_var = mapquantiles(raw_clim_var,station_lon,...
    station_lat,qmfs,raw_lon,raw_lat,bias_interp_method,bc_type,...
    qmf_period,raw_time);

%% Interpolate station trends to grid
if strcmp(preserve_trends,'yes')  
    grid_trends_interp = interpolate_trends(station_trends,...
        station_coords.lon,station_coords.lat,raw_lon,raw_lat,...
        grid_trends,bc_type);
end

%% Clear raw data to avoid OOM
clear raw_clim_var grid_trends

%% Retrend 
if strcmp(preserve_trends,'yes')
    bc_clim_var = retrend(bc_clim_var,grid_trends_interp,bc_type);
end

%% Clear interpolated grid trends and reload raw and station data
clear grid_trends_interp
[raw_clim_var,~,~,~] = loadrawdata(file_path_raw_data,clim_var_name);
[station_clim_var,station_coords,station_lat,station_lon,station_time,...
    ] = loadstationdata(file_path_station_clim_var,...
    file_path_station_coords);

%% Get raw and bias-corrected climate variables at stations
raw_clim_var_station = extract_grid_at_stations(raw_clim_var,...
    station_lon,station_lat,raw_lon,raw_lat,station_clim_var);
bc_clim_var_station = extract_grid_at_stations(bc_clim_var,...
    station_lon,station_lat,raw_lon,raw_lat,station_clim_var);

%% Make yearly versions of those tables
[station_clim_var_yearly, raw_clim_var_station_yearly, ...
    bc_clim_var_station_yearly, years] = makeyearlytables( ...
    station_clim_var, raw_clim_var_station, bc_clim_var_station, ...
    raw_time, agg_method);

%% Get linear trends
[station_trends, raw_trends, bc_trends] = getlineartrends( ...
    station_clim_var_yearly, ...
    raw_clim_var_station_yearly, ...
    bc_clim_var_station_yearly, ...
    years);

%% Make diagnostic plots
makeplots(station_clim_var, station_coords, station_time, ...
    raw_clim_var_station, bc_clim_var_station, raw_time, ...
    station_clim_var_yearly, raw_clim_var_station_yearly, ...
    bc_clim_var_station_yearly, years, station_trends, raw_trends, ...
    bc_trends, bc_clim_var, raw_lon, raw_lat, file_path_figures, ...
    clim_var_name, clim_var_long_name, clim_var_units);

%% Display averages for testing
disp(nanmean(bc_clim_var,'all'));
disp(nanmean(raw_clim_var,'all'));
disp(nanmean(table2array(station_clim_var),'all'));

%% Put bias corrected data in netcdf file
%
% Permute back to ECMWF standard
%bc_clim_var = permute(bc_clim_var,[2 1 3]);
%
% Copy file and write new data
%copyfile(file_path_raw_data,file_path_bc_data);
%ncwrite(file_path_bc_data,clim_var_name,bc_clim_var);
%
% Update documentation
%ncwriteatt(file_path_bc_data,clim_var_name,'bias_correction',...
%    'empirical quantile mapping');
%ncwriteatt(file_path_bc_data,'/','history', ...
%    sprintf('%s: replaced %s with bias-corrected data (EQM)',...
%    datestr(now,30),clim_var_name));
