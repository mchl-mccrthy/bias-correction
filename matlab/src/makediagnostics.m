% Make diagnostics
function diagnostics = makediagnostics(cfg)

% Unpack workflow configuration
clim_var_name = cfg.clim_var_name;
agg_method = cfg.agg_method;
file_path_station_coords = cfg.file_path_station_coords;
file_path_station_clim_var = cfg.file_path_station_clim_var;
file_path_raw_data = cfg.file_path_raw_data;
file_path_bc_data = cfg.file_path_bc_data;
file_path_figures_tables = cfg.file_path_figures_tables;

% Check if bias-corrected data exist
if ~isfile(file_path_bc_data)
    error('Bias-corrected data file not found: %s',file_path_bc_data)
end

% Load raw data
[raw_grid_clim_var,grid_x,grid_y,~,grid_time] = loadgriddata( ...
    file_path_raw_data,clim_var_name);

% Load bias corrected data
[bc_grid_clim_var,~,~,~,~] = loadgriddata( ...
    file_path_bc_data,clim_var_name);

% Load station data
[station_clim_var,station_coords,station_x,station_y,~,station_time] = ...
    loadstationdata(file_path_station_clim_var,file_path_station_coords);

% Get raw and bias-corrected climate variables at stations
raw_station_clim_var...
    = gridtostations(...
    raw_grid_clim_var,station_x,station_y,grid_x,grid_y,station_clim_var);
bc_station_clim_var...
    = gridtostations(...
    bc_grid_clim_var,station_x,station_y,grid_x,grid_y,station_clim_var);

% Make yearly versions of climate variables at stations
[station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years]...
    = makeyearlytables(...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,grid_time,...
    agg_method);

% Get linear trends at stations
[station_linear_trends,raw_station_linear_trends,bc_station_linear_trends]...
    = getlineartrends(...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years);

% Get quantile mean absolute errors at stations
[raw_station_quantile_mae,bc_station_quantile_mae]...
    = getquantilemae(...
    station_clim_var,raw_station_clim_var,bc_station_clim_var);

% Get annual mean absolute errors at stations
[raw_station_annual_mae,bc_station_annual_mae]...
    = getannualmae(...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly);

% Get timestep domain means of gridded data
raw_grid_domain_mean = squeeze(mean(raw_grid_clim_var,[1 2],'omitnan'));
bc_grid_domain_mean = squeeze(mean(bc_grid_clim_var,[1 2],'omitnan'));

% Make yearly gridded fields for domain summaries and plots.
[raw_grid_clim_var_yearly,grid_years] = makeyearlygrid(...
    raw_grid_clim_var,grid_time,agg_method);
[bc_grid_clim_var_yearly,~] = makeyearlygrid(...
    bc_grid_clim_var,grid_time,agg_method);

% Make summary table of station-level diagnostics
[station_means,raw_means,bc_means] = getstationmeans(...
    station_clim_var_yearly,raw_station_clim_var_yearly,bc_station_clim_var_yearly);
summary_inputs = {station_linear_trends,raw_station_linear_trends,...
    bc_station_linear_trends,raw_station_quantile_mae,...
    bc_station_quantile_mae,raw_station_annual_mae,...
    bc_station_annual_mae,station_means,raw_means,bc_means};
summary_table = makesummarytable(clim_var_name,summary_inputs{:});
summary_table(:,{'Observed_mean','Model_mean','Observed_linear_trend','Model_linear_trend'}) = [];
[raw_mean,raw_trend] = getdomainsummary(raw_grid_clim_var_yearly,grid_years);
[bc_mean,bc_trend] = getdomainsummary(bc_grid_clim_var_yearly,grid_years);
summary_table.Domain_mean_yearly = [raw_mean;bc_mean];
summary_table.Domain_linear_trend = [raw_trend;bc_trend];

% Save summary table of station-level diagnostics
file_path_overview = fullfile(file_path_figures_tables,'overview');
if ~exist(file_path_overview,'dir')
    mkdir(file_path_overview)
end
writetable(diagnosticcsvtable(summary_table,cfg),fullfile(file_path_overview,...
    [clim_var_name '_diagnostics_summary.csv']))

% Save one diagnostic table per station, alongside the station figures.
station_dir = fullfile(file_path_figures_tables,'individual_stations');
if ~exist(station_dir,'dir')
    mkdir(station_dir)
end
station_names = station_clim_var.Properties.VariableNames;
for i_station = 1:width(station_clim_var)
    station_inputs = cellfun(@(values) values(i_station),...
        summary_inputs,'UniformOutput',false);
    station_table = makesummarytable(clim_var_name,station_inputs{:});
    station_table = renamevars(station_table,'MAE_linear_trends','AE_linear_trend');
    station_table = renamevars(station_table,{'Observed_mean','Model_mean'},...
        {'Observed_mean_yearly','Model_mean_yearly'});
    station_name = station_names{i_station};
    station_table.Station = repmat({station_name},2,1);
    station_table = movevars(station_table,'Station','After','Variable');
    writetable(diagnosticcsvtable(station_table,cfg),fullfile(station_dir,...
        [station_name '_' clim_var_name '_diagnostics_summary.csv']))
end

% Get linear trends of gridded bias-corrected data
bc_grid_linear_trends = getgridlineartrends( ...
    bc_grid_clim_var_yearly,grid_years);

% Make struct of diagnostics
diagnostics.station_clim_var = station_clim_var;
diagnostics.station_coords = station_coords;
diagnostics.station_x = station_x;
diagnostics.station_y = station_y;
diagnostics.station_time = station_time;
diagnostics.raw_station_clim_var = raw_station_clim_var;
diagnostics.bc_station_clim_var = bc_station_clim_var;
diagnostics.station_clim_var_yearly = station_clim_var_yearly;
diagnostics.raw_station_clim_var_yearly = raw_station_clim_var_yearly;
diagnostics.bc_station_clim_var_yearly = bc_station_clim_var_yearly;
diagnostics.years = years;
diagnostics.station_linear_trends = station_linear_trends;
diagnostics.raw_station_linear_trends = raw_station_linear_trends;
diagnostics.bc_station_linear_trends = bc_station_linear_trends;
diagnostics.raw_station_quantile_mae = raw_station_quantile_mae;
diagnostics.bc_station_quantile_mae = bc_station_quantile_mae;
diagnostics.raw_station_annual_mae = raw_station_annual_mae;
diagnostics.bc_station_annual_mae = bc_station_annual_mae;
diagnostics.summary_table = summary_table;
diagnostics.raw_grid_domain_mean = raw_grid_domain_mean;
diagnostics.bc_grid_domain_mean = bc_grid_domain_mean;
diagnostics.raw_grid_clim_var_yearly = raw_grid_clim_var_yearly;
diagnostics.bc_grid_clim_var_yearly = bc_grid_clim_var_yearly;
diagnostics.bc_grid_linear_trends = bc_grid_linear_trends;
diagnostics.grid_x = grid_x;
diagnostics.grid_y = grid_y;
diagnostics.grid_time = grid_time;

end
