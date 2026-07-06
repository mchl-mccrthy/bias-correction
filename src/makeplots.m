% Make diagnostic plots for bias correction
function makeplots(station_clim_var,station_coords,station_time,...
    raw_station_clim_var,bc_station_clim_var,raw_time,...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years,station_linear_trends,...
    raw_station_linear_trends,bc_station_linear_trends,...
    raw_lon,raw_lat,file_path_figures,clim_var_name,clim_var_long_name,...
    clim_var_units,bc_grid_clim_var_yearly,bc_grid_linear_trends,agg_method)

% Get number of stations
n_stations = width(station_clim_var);

% Make maps of long-term average and linear trends
plotmaps(raw_lon,raw_lat,bc_grid_clim_var_yearly,...
    bc_grid_linear_trends,file_path_figures,clim_var_name,...
    clim_var_long_name,clim_var_units,agg_method);

% Make scatter plot of linear trends
plottrendcomparison(station_linear_trends,...
    raw_station_linear_trends,bc_station_linear_trends,...
    file_path_figures,clim_var_name,clim_var_long_name,clim_var_units);

% Make quantile-quantile plots for all stations
plotallstationsqq( ...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,...
    station_time,raw_time,file_path_figures,clim_var_name,...
    clim_var_long_name,clim_var_units);

% Make plot of station data availability
plotstationavailability( ...
    station_clim_var,station_coords,station_time,...
    file_path_figures,clim_var_name);

% Make plots for each station
for i_station = 1:n_stations

    % Get station name
    station_name = station_coords.station{i_station};

    % Daily time series
    figure()
    plot(raw_time, raw_station_clim_var{:,i_station}, 'g'); hold on
    plot(raw_time, bc_station_clim_var{:,i_station}, 'b')
    plot(station_time, station_clim_var{:,i_station}, 'r')
    ylabel([clim_var_long_name ' (' clim_var_units ')'])
    xlim([min(raw_time) max(raw_time)])
    title(station_name, 'Interpreter','none')
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,7,2,4)
    print(gcf, [file_path_figures '/' station_name '_' ...
        clim_var_name '_time_series.png'], '-dpng','-r300');

    % Get overlapping valid data
    [station_overlap,raw_overlap,bc_overlap] = ...
        getoverlappingstationdata( ...
        station_clim_var,raw_station_clim_var,bc_station_clim_var, ...
        station_time,raw_time,i_station);

    if isempty(station_overlap)
        continue
    end
    hist_min = min([raw_overlap; bc_overlap; station_overlap]);
    hist_max = max([raw_overlap; bc_overlap; station_overlap]);
    if hist_min == hist_max
        continue
    end

    % Histogram
    figure()
    edges = linspace(hist_min, hist_max, 25);
    histogram(raw_overlap, edges); hold on
    histogram(bc_overlap, edges)
    histogram(station_overlap, edges)
    ylabel('Count')
    xlabel([clim_var_long_name ' (' clim_var_units ')'])
    title(station_name, 'Interpreter','none')
    xlim([hist_min hist_max])
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,4,4,4)
    print(gcf, [file_path_figures '/' station_name '_' ...
        clim_var_name '_histogram.png'], '-dpng','-r300');

    % Quantile-quantile plot
    figure()
    q = linspace(0,1,1000);
    station_quantiles = quantile(station_overlap, q);
    raw_quantiles = quantile(raw_overlap, q);
    bc_quantiles = quantile(bc_overlap, q);
    plot(station_quantiles, raw_quantiles, 'r'); hold on
    plot(station_quantiles, bc_quantiles, 'b')
    grid on
    ylabel([clim_var_long_name ',' newline ...
        'raw and bias corrected (' clim_var_units ')'])
    xlabel([clim_var_long_name ', station (' clim_var_units ')'])
    title(station_name, 'Interpreter','none')
    xlim([hist_min hist_max])
    ylim([hist_min hist_max])
    legend('Raw','Bias corrected','Location','eastoutside')
    formatfigure(gcf,4,4,4)
    print(gcf, [file_path_figures '/' station_name '_' ...
        clim_var_name '_quantile-quantile.png'], '-dpng','-r300');

    % Yearly time series
    figure()
    plot(years, raw_station_clim_var_yearly{:,i_station}, 'g'); hold on
    plot(years, bc_station_clim_var_yearly{:,i_station}, 'b')
    plot(years, station_clim_var_yearly{:,i_station}, 'r')
    ylabel([clim_var_long_name ' (' clim_var_units ')'])
    xlim([min(years) max(years)])
    title(station_name, 'Interpreter','none')
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,7,2,4)
    print(gcf, [file_path_figures '/' station_name '_' ...
        clim_var_name '_time_series_yearly.png'], '-dpng','-r300');
end

end