% Plot domain-mean annual time series of gridded data
function plotoverviewtimeseries(raw_grid_clim_var_yearly,...
    bc_grid_clim_var_yearly,years,file_path_figures_tables,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method)

% Get yearly units
annual_units = yearlyunits(clim_var_units,agg_method);

% Calculate domain means
raw_domain_mean = squeeze(mean(raw_grid_clim_var_yearly,[1 2],'omitnan'));
bc_domain_mean = squeeze(mean(bc_grid_clim_var_yearly,[1 2],'omitnan'));

% Make plot
figure()
plot(years,raw_domain_mean,'Color',[0.45 0.45 0.45]); hold on
plot(years,bc_domain_mean,'r')
ylabel([clim_var_long_name ' (' annual_units ')'])
xlim([min(years) max(years)])
title('Domain spatial average, yearly')
legend({'Raw','Bias-corrected'},'Location','eastoutside')
formatfigure(gcf,7,2,4)
print(gcf,fullfile(file_path_figures_tables,[clim_var_name ...
    '_domain_mean_time_series_yearly.png']),'-dpng','-r300');

end
