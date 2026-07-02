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
    'make_plots', ...
    'n_quantiles', ...
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
mustbeoneof(cfg.preserve_trends,{'yes','no'},'preserve_trends')
mustbeoneof(cfg.agg_method,{'mean','sum'},'agg_method')

% Validate numeric/logical settings
if ~isscalar(cfg.trend_window) || cfg.trend_window <= 0
    error('cfg.trend_window must be a positive scalar.')
end

if ~islogical(cfg.write_output) || ~isscalar(cfg.write_output)
    error('cfg.write_output must be a scalar logical: true or false.')
end

if ~islogical(cfg.make_plots) || ~isscalar(cfg.make_plots)
    error('cfg.make_plots must be a scalar logical: true or false.')
end

if ~isscalar(cfg.n_quantiles) || cfg.n_quantiles <= 1 || ...
        cfg.n_quantiles ~= round(cfg.n_quantiles)
    error('cfg.n_quantiles must be an integer scalar greater than 1.')
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

% Validate output locations
if cfg.write_output
    output_folder = fileparts(cfg.file_path_bc_data);
    if ~isfolder(output_folder)
        error('Output data folder not found: %s',output_folder)
    end
end

if cfg.make_plots
    if ~isfolder(cfg.file_path_figures)
        error('Figures folder not found: %s',cfg.file_path_figures)
    end
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