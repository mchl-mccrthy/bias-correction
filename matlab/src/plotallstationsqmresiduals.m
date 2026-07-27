% Make quantile-mapping residual plot for all stations
function plotallstationsqmresiduals(station_clim_var,raw_station_clim_var,...
    bc_station_clim_var,station_time,grid_time,file_path_figures,...
    clim_var_name,clim_var_long_name,clim_var_units)

% Make plot
figure()
q = linspace(0,1,1000);
x_min = Inf;
x_max = -Inf;
residual_max = 0;
h_raw = [];
h_bc = [];
n_stations = width(station_clim_var);
for i_station = 1:n_stations
    [station_overlap,raw_overlap,bc_overlap] = ...
        getoverlappingstationdata( ...
        station_clim_var,raw_station_clim_var,bc_station_clim_var, ...
        station_time,grid_time,i_station);
    if isempty(station_overlap)
        continue
    end
    station_quantiles = quantile(station_overlap, q);
    raw_quantiles = quantile(raw_overlap, q);
    bc_quantiles = quantile(bc_overlap, q);
    raw_residuals = raw_quantiles - station_quantiles;
    bc_residuals = bc_quantiles - station_quantiles;
    if isempty(h_raw)
        h_raw = plot(station_quantiles, raw_residuals, ...
            'Color',[0.45 0.45 0.45]); hold on
        h_bc = plot(station_quantiles, bc_residuals, 'r');
    else
        plot(station_quantiles, raw_residuals, ...
            'Color',[0.45 0.45 0.45]); hold on
        plot(station_quantiles, bc_residuals, 'r')
    end
    x_min = min([x_min; station_quantiles(:)]);
    x_max = max([x_max; station_quantiles(:)]);
    residual_max = max([residual_max; abs(raw_residuals(:)); ...
        abs(bc_residuals(:))]);
end
ylabel([clim_var_long_name ' residual (' clim_var_units ')'])
xlabel([clim_var_long_name ', station (' clim_var_units ')'])
title('All stations, quantile residuals')
if isfinite(x_min) && isfinite(x_max) && x_min < x_max
    x_pad = 0.05 * (x_max - x_min);
    xlim([x_min - x_pad x_max + x_pad])
end
if isfinite(residual_max) && residual_max > 0
    ylim([-1.05 * residual_max 1.05 * residual_max])
end
h_zero = yline(0,'k:',...
    'HandleVisibility','off');
uistack(h_zero,'bottom');
if ~isempty(h_raw)
    legend([h_raw h_bc],{'Raw','Bias-corrected'},'Location','eastoutside')
end
formatfigure(gcf,4,2,4)
print(gcf,fullfile(file_path_figures, [clim_var_name ...
    '_all_stations_qm_residuals.png']), '-dpng','-r300');

end
