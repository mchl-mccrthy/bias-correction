% Plot maps of long-term averages and linear trends
function plotmaps(raw_lon,raw_lat,bc_grid_clim_var_yearly,...
    bc_grid_linear_trends,file_path_figures,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method)

% Plot map of long-term average of bias-corrected data
figure()
contourf(raw_lon,raw_lat,mean(bc_grid_clim_var_yearly,3),100, ...
    'LineColor','none')
c = colorbar;
if strcmp(agg_method,'sum')
    c.Label.String = [clim_var_long_name ' (' clim_var_units ' year^{-1})'];
elseif strcmp(agg_method,'mean')
    c.Label.String = [clim_var_long_name ' (' clim_var_units ')'];
end
title('Long-term average')
ll_ratio = (max(raw_lon,[],'all') - min(raw_lon,[],'all')) ./ ...
           (max(raw_lat,[],'all') - min(raw_lat,[],'all'));
formatfigure(gcf,4,4/ll_ratio,2)
print(gcf, fullfile(file_path_figures, [clim_var_name ...
    '_long_term_average_map.png']), '-dpng','-r300');

% Plot map of long-term linear trends of bias-corrected data
figure()
contourf(raw_lon,raw_lat,bc_grid_linear_trends,100,'LineColor','none')
c = colorbar;
if strcmp(agg_method,'sum')
    c.Label.String = [clim_var_long_name ' trend (' clim_var_units ' year^{-2})'];
elseif strcmp(agg_method,'mean')
    c.Label.String = [clim_var_long_name ' trend (' clim_var_units ' year^{-1})'];
end
title('Long-term trend')
ll_ratio = (max(raw_lon,[],'all') - min(raw_lon,[],'all')) ./ ...
           (max(raw_lat,[],'all') - min(raw_lat,[],'all'));
formatfigure(gcf,4,4/ll_ratio,2)
print(gcf, fullfile(file_path_figures, [clim_var_name ...
    '_bc_linear_trend_map.png']), '-dpng','-r300');
end