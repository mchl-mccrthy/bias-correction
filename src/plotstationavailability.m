% Plot station availability
function plotstationavailability(station_clim_var,station_coords,...
    station_time,file_path_figures,clim_var_name)

figure()
n_stations = width(station_clim_var);
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
print(gcf, fullfile(file_path_figures, [clim_var_name ...
    '_station_availability.png']), '-dpng','-r300');

end