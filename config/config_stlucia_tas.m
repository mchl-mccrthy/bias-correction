function cfg = config_stlucia_tas()

% Variable settings
cfg.clim_var_name = 'tas';
cfg.clim_var_long_name = 'Temperature';
cfg.clim_var_units = 'K';
cfg.qmf_period = 'monthly'; % 'whole', 'seasonal', or 'monthly'
cfg.bc_type = 'additive'; % 'additive' or 'multiplicative'
cfg.preserve_trends = true; % true or false
cfg.trend_window = 365*5; % Moving mean window in time steps
cfg.agg_method = 'mean'; % 'mean' or 'sum'
cfg.write_output = false;
cfg.make_plots = true;
cfg.n_quantiles = 1001; % Number of quantiles for QMFs
cfg.idw_power = 2; % Inverse distance weighting distance exponent
cfg.multiplicative_epsilon = 0.1; % Offset for multiplicative detrending/retrending

% File paths
cfg.file_path_station_coords = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\stations\StLucia_coordinates.csv';
cfg.file_path_station_clim_var = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\stations\StLucia_tas.csv';
cfg.file_path_raw_data = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\chelsa\tas_StLucia_1981_2020.nc';
cfg.file_path_bc_data = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\processed\key_variables\reanalysis\tas_bc_StLucia_1981_2020.nc';
cfg.file_path_figures = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\temp\';

end