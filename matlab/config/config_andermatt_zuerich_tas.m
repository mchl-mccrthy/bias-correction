function cfg = config_andermatt_zuerich_tas()

% Repository root
config_path = fileparts(mfilename('fullpath'));
repo_root = fileparts(fileparts(config_path));

% Variable settings
cfg.clim_var_name = 'tas';
cfg.clim_var_long_name = 'Temperature';
cfg.clim_var_units = '\circC';
cfg.qmf_period = 'monthly'; % 'whole', 'seasonal', or 'monthly'
cfg.bc_type = 'additive'; % 'additive' or 'multiplicative'
cfg.trend_method = 'grid'; % 'station', 'grid', or 'none'
cfg.trend_window = 365*5; % Moving mean window in time steps
cfg.agg_method = 'mean'; % 'mean' or 'sum'
cfg.write_output = true;
cfg.n_quantiles = 1001; % Number of quantiles for QMFs
cfg.idw_power = 2; % Inverse distance weighting distance exponent
cfg.idw_method = 'elevation_aware'; % 'horizontal' or 'elevation_aware'
cfg.idw_alpha = 10; % 100 m vertical = 1 km horizontal
cfg.multiplicative_epsilon = 0.1; % Offset for multiplicative detrending/retrending
cfg.use_parallel = false;
cfg.n_workers = []; % [], 2, 3 ...
cfg.keep_grid_biases = false;
cfg.coordinate_system = 'geographic'; % 'geographic' or 'projected'

% File paths
cfg.file_path_station_coords = fullfile(repo_root,'input_data','andermatt_zuerich_1981_2019','station','andermatt_zuerich_coordinates.csv');
cfg.file_path_station_clim_var = fullfile(repo_root,'input_data','andermatt_zuerich_1981_2019','station','andermatt_zuerich_tas.csv');
cfg.file_path_raw_data = fullfile(repo_root,'input_data','andermatt_zuerich_1981_2019','gridded','tas_andermatt_zuerich_1981_2019.nc');
cfg.file_path_bc_data = fullfile(repo_root,'output_data','andermatt_zuerich_1981_2019','gridded','tas_bc_andermatt_zuerich_1981_2019.nc');
cfg.file_path_figures = fullfile(repo_root,'output_data','andermatt_zuerich_1981_2019','figures');

end
