% Make diagnostic plots for bias correction
function makeplots(station_clim_var,station_coords,station_time,...
    raw_station_clim_var,bc_station_clim_var,raw_time,...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years,station_linear_trends,...
    raw_station_linear_trends,bc_station_linear_trends,bc_grid_clim_var,...
    raw_lon,raw_lat,file_path_figures,clim_var_name,clim_var_long_name,...
    clim_var_units)

% Plot map of bias-corrected data
figure()
contourf(raw_lon,raw_lat,mean(bc_grid_clim_var,3),100, ...
    'LineColor','none')
c = colorbar;
c.Label.String = [clim_var_long_name ' (' clim_var_units ')'];
title('Long-term average')
ll_ratio = (max(raw_lon,[],'all') - min(raw_lon,[],'all')) ./ ...
           (max(raw_lat,[],'all') - min(raw_lat,[],'all'));
formatfigure(gcf,4,4/ll_ratio,2)
print(gcf, [file_path_figures '/' clim_var_name ...
    '_long-term_average.png'], '-dpng','-r300');

% Plot trends
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

% Get number of stations
n_stations = width(station_clim_var);

% Plot station availability
figure()
for i_station = 1:n_stations
    scatter(station_time, ...
        station_clim_var{:,i_station} ./ station_clim_var{:,i_station} ...
        * i_station, 'blue'); 
    hold on
    text(station_time(end)+calyears(1), i_station, ...
        station_coords.station{i_station}, ...
        'Interpreter','none', 'FontSize',7)
end
xlim([station_time(1) station_time(end)])
ylim([0 n_stations+1])
yticklabels([])
formatfigure(gcf,5,3,4)
print(gcf, [file_path_figures '/' clim_var_name ...
    '_station_availability.png'], '-dpng','-r300');

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
    raw_tmp = raw_station_clim_var{:,i_station};
    bc_tmp = bc_station_clim_var{:,i_station};
    station_tmp = station_clim_var{:,i_station};
    [~, ia, ib] = intersect(raw_time, station_time);
    raw_overlap = raw_tmp(ia);
    bc_overlap = bc_tmp(ia);
    station_overlap = station_tmp(ib);
    valid = ~isnan(raw_overlap) & ...
            ~isnan(bc_overlap) & ...
            ~isnan(station_overlap);
    raw_overlap = raw_overlap(valid);
    bc_overlap = bc_overlap(valid);
    station_overlap = station_overlap(valid);
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
    if contains(clim_var_name,'pr')
        xlim([0 50])
    else
        xlim([hist_min hist_max])
    end
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
    if contains(clim_var_name,'pr')
        xlim([0 50])
        ylim([0 50])
    else
        xlim([hist_min hist_max])
        ylim([hist_min hist_max])
    end
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