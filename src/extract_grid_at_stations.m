function clim_var_station = extract_grid_at_stations(clim_var, station_lon, station_lat, grid_lon, grid_lat, template_table)

% Extract nearest grid-cell time series at station locations.

n_stations = numel(station_lon);
n_time_steps = size(clim_var,3);

clim_var_station = template_table;
clim_var_station{:,:} = nan(n_time_steps,n_stations);

for i_station = 1:n_stations

    [row,col] = indexofclosest2( ...
        station_lon(i_station), ...
        station_lat(i_station), ...
        grid_lon, ...
        grid_lat);

    clim_var_station{:,i_station} = squeeze(clim_var(row,col,:));

end

end
