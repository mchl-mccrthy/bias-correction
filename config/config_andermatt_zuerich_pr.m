function cfg = config_andermatt_zuerich_pr()

% Variable settings
cfg.clim_var_name = 'pr';
cfg.clim_var_long_name = 'Precipitation';
cfg.clim_var_units = 'mm';
cfg.qmf_period = 'monthly'; % 'whole', 'seasonal', or 'monthly'
cfg.bc_type = 'multiplicative'; % 'additive' or 'multiplicative'
cfg.preserve_trends = true; % true or false
cfg.trend_window = 365*5; % Moving mean window in time steps
cfg.agg_method = 'sum'; % 'mean' or 'sum'
cfg.write_output = true;
cfg.n_quantiles = 1001; % Number of quantiles for QMFs
cfg.idw_power = 2; % Inverse distance weighting distance exponent
cfg.idw_method = 'elevation_aware'; % 'horizontal' or 'elevation_aware'
cfg.idw_alpha = 10; % 100 m vertical = 1000 m horizontal (1000/100 = 10)
cfg.multiplicative_epsilon = 0.1; % Offset for multiplicative detrending/retrending
cfg.use_parallel = false;
cfg.n_workers = []; % [], 2, 3 ...
cfg.keep_grid_biases = false;
cfg.coordinate_system = 'geographic'; % 'geographic' or 'projected'

% File paths
cfg.file_path_station_coords = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\input_data\meteoswiss\processed\andermatt_zuerich_coordinates.csv';
cfg.file_path_station_clim_var = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\input_data\meteoswiss\processed\andermatt_zuerich_pr.csv';
cfg.file_path_raw_data = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\input_data\chelsa\processed\andermatt_zuerich_1981_2019\pr_andermatt_zuerich_1981_2019.nc';
cfg.file_path_bc_data = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\output_data\andermatt_zuerich_1981_2019\pr_bc_andermatt_zuerich_1981_2019.nc';
cfg.file_path_figures = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\output_data\figures\';

end