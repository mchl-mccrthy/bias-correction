% QC CHELSA and station data

var_name = 'tasmin';
project_name = 'Armenia_1981_2020';
country_name = 'Armenia';
root = 'C:\Users\McCarthy\Desktop\bias_correction\';

%% Get station data

station_path = [root 'input_data\station_data\Armenia\proc_data\' country_name '_' var_name '.csv'];
var_stations = readtable(station_path);
var_stations = table2array(var_stations);

%% Plot station data

figure()
plot(var_stations(1:end,4:end))
title('Stations')

%% Get CHELSA

chelsa_path = [root 'input_data\climate_data\' project_name '\' var_name '_' project_name '.nc'];
var_chelsa = ncread(chelsa_path,var_name);
[nx,ny,nt] = size(var_chelsa);
var_chelsa = reshape(var_chelsa,nx*ny,nt);
var_chelsa_mean = mean(var_chelsa,1);
var_chelsa_max = max(var_chelsa,[],1);
var_chelsa_min = min(var_chelsa,[],1);

%% Plot CHELSA

figure()
plot(var_chelsa_mean)
title('mean(CHELSA)')

figure()
plot(var_chelsa_min)
title('min(CHELSA)')

figure()
plot(var_chelsa_max)
title('max(CHELSA)')