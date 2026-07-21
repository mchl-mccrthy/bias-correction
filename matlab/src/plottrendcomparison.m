% Make scatter plot of linear trends
function plottrendcomparison(station_linear_trends,...
    raw_station_linear_trends,bc_station_linear_trends,...
    file_path_figures,clim_var_name,clim_var_long_name,clim_var_units,...
    agg_method)

% Get trend units
if strcmp(agg_method,'sum')
    trend_units = [clim_var_units ' year^{-2}'];
else
    trend_units = [clim_var_units ' year^{-1}'];
end

% Make plot
figure()
lims = [min([station_linear_trends raw_station_linear_trends ...
    bc_station_linear_trends 0]), ...
        max([station_linear_trends raw_station_linear_trends ...
        bc_station_linear_trends 0])];
plot(lims,lims,'k:','HandleVisibility','off'); hold on
scatter(station_linear_trends,raw_station_linear_trends,'filled')
scatter(station_linear_trends,bc_station_linear_trends,'filled')
xlabel([clim_var_long_name ' trend, stations (' ...
    trend_units ')'])
ylabel([clim_var_long_name ' trend, gridded (' ...
    trend_units ')'])
xlim(lims)
ylim(lims)
legend('Raw','Bias-corrected','Location','eastoutside')
formatfigure(gcf,4,4,4)
print(gcf,fullfile(file_path_figures,[clim_var_name ...
    '_linear_trends_scatter.png']),'-dpng','-r300');

end

