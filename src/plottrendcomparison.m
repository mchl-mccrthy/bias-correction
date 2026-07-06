% Make scatter plot of linear trends
function plottrendcomparison(station_linear_trends,...
    raw_station_linear_trends,bc_station_linear_trends,...
    file_path_figures,clim_var_name,clim_var_long_name,clim_var_units)

figure()
scatter(station_linear_trends, raw_station_linear_trends); hold on
scatter(station_linear_trends, bc_station_linear_trends)
xlabel([clim_var_long_name ' trend, stations (' ...
    clim_var_units ' year^{-1})'])
ylabel([clim_var_long_name ' trend, gridded (' ...
    clim_var_units ' year^{-1})'])
lims = [min([station_linear_trends raw_station_linear_trends bc_station_linear_trends 0]), ...
        max([station_linear_trends raw_station_linear_trends bc_station_linear_trends 0])];
xlim(lims)
ylim(lims)
legend('Raw','Bias corrected','Location','eastoutside')
formatfigure(gcf,4,4,4)
print(gcf, [file_path_figures '/' clim_var_name ...
    '_trends.png'], '-dpng','-r300');

end

