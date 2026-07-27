% Plot domain-mean timestep time series of gridded data
function plotoverviewtimesteptimeseries(raw_grid_domain_mean,...
    bc_grid_domain_mean,grid_time,file_path_figures_tables,clim_var_name,...
    clim_var_long_name,clim_var_units)

% Make plot
figure()
plot(grid_time,raw_grid_domain_mean,'Color',[0.45 0.45 0.45]); hold on
plot(grid_time,bc_grid_domain_mean,'r')
ylabel([clim_var_long_name ' (' clim_var_units ')'])
xlim([grid_time(1) grid_time(end)])
title('Domain spatial average, time step')
legend({'Raw','Bias-corrected'},'Location','eastoutside')
formatfigure(gcf,7,2,4)
print(gcf,fullfile(file_path_figures_tables,[clim_var_name ...
    '_domain_mean_time_series.png']),'-dpng','-r300');

end
