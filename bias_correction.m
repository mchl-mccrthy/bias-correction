% Bias correct climate data

% Notes
% - Raw climate data need to be stored: x/lon/longitude, y/lat/latitude, 
%   time. This is the standard used by ECMWF.
% - Station data are assumed to be in same time zone as gridded climate 
%   data.
% - Station data should cover the same time period as the gridded data, 
%   without any missing days, but NaNs are allowed.
% - clim_var_name should be the same in both station data and NetCDF file.

% Add paths
addpath('src')
addpath(genpath(fullfile('src','third_party')))
addpath('config')

% Load configuration
cfg = config_stlucia_tas();

% Run bias correction
results = runbiascorrection(cfg);

% Make diagnostics
diagnostics = makediagnostics(cfg);

% Plot results
makeplots(diagnostics,cfg);