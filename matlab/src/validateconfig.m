% Validate configuration
function validateconfig(cfg)

% Check that all required fields exist
required_fields = { ...
    'clim_var_name', ...
    'clim_var_long_name', ...
    'clim_var_units', ...
    'qmf_period', ...
    'bc_type', ...
    'preserve_trends', ...
    'trend_window', ...
    'agg_method', ...
    'write_output', ...
    'n_quantiles', ...
    'idw_power', ...
    'idw_method', ...
    'idw_alpha', ...
    'use_parallel', ...
    'n_workers', ...
    'multiplicative_epsilon', ...
    'keep_grid_biases', ...
    'coordinate_system', ...
    'file_path_station_coords', ...
    'file_path_station_clim_var', ...
    'file_path_raw_data', ...
    'file_path_bc_data', ...
    'file_path_figures'};

n_fields = numel(required_fields);
for i_field = 1:n_fields
    if ~isfield(cfg,required_fields{i_field})
        error('Missing required config field: %s',required_fields{i_field})
    end
end

% Validate options
mustbeoneof(cfg.qmf_period,{'whole','seasonal','monthly'},'qmf_period')
mustbeoneof(cfg.bc_type,{'additive','multiplicative'},'bc_type')
mustbeoneof(cfg.agg_method,{'mean','sum'},'agg_method')
mustbeoneof(cfg.coordinate_system,{'geographic','projected'},'coordinate_system')
mustbeoneof(cfg.idw_method,{'horizontal','elevation_aware'},'idw_method')

if ~isscalar(cfg.idw_alpha) || cfg.idw_alpha <= 0
    error('cfg.idw_alpha must be a positive scalar.')
end

% Validate numeric/logical settings
if ~isscalar(cfg.trend_window) || cfg.trend_window <= 0
    error('cfg.trend_window must be a positive scalar.')
end

if ~islogical(cfg.write_output) || ~isscalar(cfg.write_output)
    error('cfg.write_output must be a scalar logical: true or false.')
end

if ~isscalar(cfg.n_quantiles) || cfg.n_quantiles <= 1 || ...
        cfg.n_quantiles ~= round(cfg.n_quantiles)
    error('cfg.n_quantiles must be an integer scalar greater than 1.')
end

if ~islogical(cfg.preserve_trends) || ~isscalar(cfg.preserve_trends)
    error('cfg.preserve_trends must be a scalar logical: true or false.')
end

if ~isscalar(cfg.idw_power) || cfg.idw_power <= 0
    error('cfg.idw_power must be a positive scalar.')
end

if ~isscalar(cfg.multiplicative_epsilon) || cfg.multiplicative_epsilon < 0
    error('cfg.multiplicative_epsilon must be a non-negative scalar.')
end

if ~islogical(cfg.use_parallel) || ~isscalar(cfg.use_parallel)
    error('cfg.use_parallel must be a scalar logical: true or false.')
end

if ~(isempty(cfg.n_workers) || ...
        (isscalar(cfg.n_workers) && ...
         cfg.n_workers == round(cfg.n_workers) && ...
         cfg.n_workers > 0))
    error('cfg.n_workers must be empty or a positive integer scalar.')
end

if ~islogical(cfg.keep_grid_biases) || ~isscalar(cfg.keep_grid_biases)
    error('cfg.keep_grid_biases must be a scalar logical: true or false.')
end

% Validate input files
if ~isfile(cfg.file_path_station_coords)
    error('Station coordinates file not found: %s',cfg.file_path_station_coords)
end

if ~isfile(cfg.file_path_station_clim_var)
    error('Station climate data file not found: %s',cfg.file_path_station_clim_var)
end

if ~isfile(cfg.file_path_raw_data)
    error('Raw climate data file not found: %s',cfg.file_path_raw_data)
end

% Helper function for verifying options
function mustbeoneof(value,allowed_values,field_name)

if ~ischar(value) && ~isstring(value)
    error('cfg.%s must be text.',field_name)
end

if ~any(strcmp(value,allowed_values))
    error('cfg.%s must be one of: %s', ...
        field_name,strjoin(allowed_values,', '))
end

end

end
