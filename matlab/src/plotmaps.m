% Plot maps of long-term averages and linear trends
function plotmaps(grid_x,grid_y,station_x,station_y,bc_grid_clim_var_yearly,...
    bc_grid_linear_trends,file_path_figures,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method)

% Plot map of long-term average of bias-corrected data
figure()
contourf(grid_x,grid_y,mean(bc_grid_clim_var_yearly,3),100, ...
    'LineColor','none')
c = colorbar;
if strcmp(agg_method,'sum')
    c.Label.String = [clim_var_long_name ' (' clim_var_units ' year^{-1})'];
elseif strcmp(agg_method,'mean')
    c.Label.String = [clim_var_long_name ' (' clim_var_units ')'];
end
hold on
h_stations = scatter(station_x,station_y,36,'o', ...
    'MarkerFaceColor','w','MarkerEdgeColor','k');
legend(h_stations,'Stations','Location','southoutside')
title('Long-term average')
ll_ratio = (max(grid_x,[],'all')-min(grid_x,[],'all'))./ ...
           (max(grid_y,[],'all')-min(grid_y,[],'all'));
formatfigure(gcf,4,4/ll_ratio,2)
print(gcf, fullfile(file_path_figures, [clim_var_name ...
    '_long_term_average_map.png']), '-dpng','-r300');

% Plot map of long-term linear trends of bias-corrected data
figure()
contourf(grid_x,grid_y,bc_grid_linear_trends,100,'LineColor','none')
c = colorbar;
if strcmp(agg_method,'sum')
    c.Label.String = [clim_var_long_name ' trend (' clim_var_units ' year^{-2})'];
elseif strcmp(agg_method,'mean')
    c.Label.String = [clim_var_long_name ' trend (' clim_var_units ' year^{-1})'];
end
hold on
h_stations = scatter(station_x,station_y,36,'o', ...
    'MarkerFaceColor','w','MarkerEdgeColor','k');
legend(h_stations,'Stations','Location','southoutside')
title('Long-term trend')
ll_ratio = (max(grid_x,[],'all')-min(grid_x,[],'all'))./ ...
           (max(grid_y,[],'all')-min(grid_y,[],'all'));
formatfigure(gcf,4,4/ll_ratio,2)
print(gcf, fullfile(file_path_figures, [clim_var_name ...
    '_bc_linear_trend_map.png']), '-dpng','-r300');
end
