% Bias correct climate data

% Notes
% - Raw climate data need to be stored: lon, lat, time. This is the 
%   standard used by ECMWF.
% - Station data are assumed to be in same time zone as gridded climate 
%   data.
% - Station data should cover the same time period as the gridded data, 
%   without any missing days. NaNs are allowed.

% Add paths
addpath(genpath('src'))
addpath(genpath('config'))

% Load configuration
cfg = config_stlucia_tas();

% Run bias correction
results = runbiascorrection(cfg);
