% Plot maps of long-term averages and linear trends
function plotmaps(grid_x,grid_y,station_x,station_y,bc_grid_clim_var_yearly,...
    bc_grid_linear_trends,file_path_figures_tables,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method,coordinate_system)

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
h_stations = scatter(station_x,station_y,10,'o', ...
    'MarkerFaceColor','w','MarkerEdgeColor','k');
legend(h_stations,'Stations','Location','southoutside')
title('Domain temporal average')
[plot_width,plot_height,lon_scale] = mapplotsize(grid_x,grid_y,coordinate_system);
daspect([1/lon_scale 1 1])
formatfigure(gcf,plot_width,plot_height,2)
print(gcf, fullfile(file_path_figures_tables, [clim_var_name ...
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
h_stations = scatter(station_x,station_y,10,'o', ...
    'MarkerFaceColor','w','MarkerEdgeColor','k');
legend(h_stations,'Stations','Location','southoutside')
title('Domain linear trend')
[plot_width,plot_height,lon_scale] = mapplotsize(grid_x,grid_y,coordinate_system);
daspect([1/lon_scale 1 1])
formatfigure(gcf,plot_width,plot_height,2)
print(gcf, fullfile(file_path_figures_tables, [clim_var_name ...
    '_bc_linear_trend_map.png']), '-dpng','-r300');
end

% Get map plot size and longitude scaling
function [plot_width,plot_height,lon_scale] = mapplotsize(grid_x,grid_y,coordinate_system)

% Get coordinate ranges
x_range = max(grid_x,[],'all') - min(grid_x,[],'all');
y_range = max(grid_y,[],'all') - min(grid_y,[],'all');

% Scale longitude distances for geographic coordinates
lon_scale = 1;
if strcmp(coordinate_system,'geographic')
    mean_lat = 0.5 * (min(grid_y,[],'all') + max(grid_y,[],'all'));
    lon_scale = cosd(mean_lat);
end

% Calculate plot size from fixed map area
map_area = 25;
map_ratio = x_range * lon_scale / y_range;
plot_width = sqrt(map_area * map_ratio);
plot_height = sqrt(map_area / map_ratio);

end
