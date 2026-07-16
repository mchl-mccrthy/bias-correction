% Get gridded climate variable time series at stations
function clim_var_station = gridtostations(clim_var,station_x,station_y,grid_x,grid_y,template_table)

% Get number of stations and number of time steps
n_stations = numel(station_x);
n_time_steps = size(clim_var,3);

% Use and format template table
clim_var_station = template_table;
clim_var_station{:,:} = nan(n_time_steps,n_stations);

% Loop through stations getting climate variable
for i_station = 1:n_stations
    [row,col] = indexofclosest2(station_x(i_station),...
        station_y(i_station),grid_x,grid_y);
    clim_var_station{:,i_station} = squeeze(clim_var(row,col,:));
end

end
