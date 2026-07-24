% Make quantile-quantile plot for all stations
function plotallstationsqq(station_clim_var,raw_station_clim_var,...
    bc_station_clim_var,station_time,grid_time,file_path_figures,...
    clim_var_name,clim_var_long_name,clim_var_units)

% Make plot
figure()
q = linspace(0,1,1000);
qq_min = Inf;
qq_max = -Inf;
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
    if isempty(h_raw)
        h_raw = plot(station_quantiles, raw_quantiles, ...
            'Color',[0.45 0.45 0.45]); hold on
        h_bc = plot(station_quantiles, bc_quantiles, 'r');
    else
        plot(station_quantiles, raw_quantiles, ...
            'Color',[0.45 0.45 0.45]); hold on
        plot(station_quantiles, bc_quantiles, 'r')
    end
    qq_min = min([qq_min; station_quantiles(:); raw_quantiles(:); bc_quantiles(:)]);
    qq_max = max([qq_max; station_quantiles(:); raw_quantiles(:); bc_quantiles(:)]);
end
ylabel([clim_var_long_name ', gridded (' clim_var_units ')'])
xlabel([clim_var_long_name ', station (' clim_var_units ')'])
title('Quantile-quantile')
if isfinite(qq_min) && isfinite(qq_max) && qq_min < qq_max
    xlim([qq_min qq_max])
    ylim([qq_min qq_max])
    h_eq = plot([qq_min qq_max],[qq_min qq_max],'k:',...
        'HandleVisibility','off');
    uistack(h_eq,'bottom');
end
if ~isempty(h_raw)
    legend([h_raw h_bc],{'Raw','Bias-corrected'},'Location','eastoutside')
end
formatfigure(gcf,4,4,4)
print(gcf,fullfile(file_path_figures, [clim_var_name ...
    '_all_stations_qq.png']), '-dpng','-r300');

end
