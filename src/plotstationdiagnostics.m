% Plot diagnostics for each station
function plotstationdiagnostics(station_clim_var,station_coords,...
    station_time,raw_station_clim_var,bc_station_clim_var,grid_time,...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years,file_path_figures,...
    clim_var_name,clim_var_long_name,clim_var_units)

% Loop through stations
n_stations = width(station_clim_var);
for i_station = 1:n_stations

    % Get station name
    station_name = station_coords.station{i_station};

    % Plot daily time series
    figure()
    plot(grid_time,raw_station_clim_var{:,i_station},'g'); hold on
    plot(grid_time,bc_station_clim_var{:,i_station},'b')
    plot(station_time,station_clim_var{:,i_station},'r')
    ylabel([clim_var_long_name ' (' clim_var_units ')'])
    xlim([min(grid_time) max(grid_time)])
    title(station_name,'Interpreter','none')
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,7,2,4)
    print(gcf,fullfile(file_path_figures,[station_name '_' clim_var_name ...
        '_time_series.png']),'-dpng','-r300');

    % Get overlapping valid data
    [station_overlap,raw_overlap,bc_overlap] = ...
        getoverlappingstationdata( ...
        station_clim_var,raw_station_clim_var,bc_station_clim_var,...
        station_time,grid_time,i_station);
    if isempty(station_overlap)
        continue
    end
    hist_min = min([raw_overlap; bc_overlap; station_overlap]);
    hist_max = max([raw_overlap; bc_overlap; station_overlap]);
    if hist_min == hist_max
        continue
    end

    % Plot histogram
    figure()
    edges = linspace(hist_min,hist_max,25);
    histogram(raw_overlap,edges); hold on
    histogram(bc_overlap,edges)
    histogram(station_overlap,edges)
    ylabel('Count')
    xlabel([clim_var_long_name ' (' clim_var_units ')'])
    title(station_name,'Interpreter','none')
    xlim([hist_min hist_max])
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,4,4,4)
    print(gcf,fullfile(file_path_figures,[station_name '_' clim_var_name ...
        '_histogram.png']),'-dpng','-r300');

    % Make quantile-quantile plot
    figure()
    q = linspace(0,1,1000);
    station_quantiles = quantile(station_overlap,q);
    raw_quantiles = quantile(raw_overlap,q);
    bc_quantiles = quantile(bc_overlap,q);
    plot(station_quantiles,raw_quantiles,'r'); hold on
    plot(station_quantiles,bc_quantiles,'b')
    grid on
    ylabel([clim_var_long_name ',' newline ...
        'raw and bias corrected (' clim_var_units ')'])
    xlabel([clim_var_long_name ',station (' clim_var_units ')'])
    title(station_name,'Interpreter','none')
    xlim([hist_min hist_max])
    ylim([hist_min hist_max])
    legend('Raw','Bias corrected','Location','eastoutside')
    formatfigure(gcf,4,4,4)
    print(gcf,fullfile(file_path_figures,[station_name '_' clim_var_name ...
        '_qq.png']),'-dpng','-r300');

    % Plot yearly time series
    figure()
    plot(years,raw_station_clim_var_yearly{:,i_station},'g'); hold on
    plot(years,bc_station_clim_var_yearly{:,i_station},'b')
    plot(years,station_clim_var_yearly{:,i_station},'r')
    ylabel([clim_var_long_name ' (' clim_var_units ')'])
    xlim([min(years) max(years)])
    title(station_name,'Interpreter','none')
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,7,2,4)
    print(gcf,fullfile(file_path_figures,[station_name '_' clim_var_name ...
        '_time_series_yearly.png']),'-dpng','-r300');
end

end