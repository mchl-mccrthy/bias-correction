% Calculate linear trends from yearly climate data data
function [station_trends,raw_trends,bc_trends] = getlineartrends(...
    station_clim_var_yearly,raw_clim_var_station_yearly,...
    bc_clim_var_station_yearly,years)

% Get number of stations
n_stations = width(station_clim_var_yearly);

% Preallocate
station_trends = nan(1,n_stations);
raw_trends = nan(1,n_stations);
bc_trends = nan(1,n_stations);

% Loop through stations
for i_station = 1:n_stations

    % Extract data
    station_tmp = station_clim_var_yearly{:,i_station};
    raw_tmp = raw_clim_var_station_yearly{:,i_station};
    bc_tmp = bc_clim_var_station_yearly{:,i_station};

    % Keep only years where all three datasets are available
    valid = ~isnan(station_tmp) & ...
            ~isnan(raw_tmp) & ...
            ~isnan(bc_tmp);

    % Only compute trends if more than two years
    if sum(valid) >= 2

        % Fit linear regressions
        station_p = polyfit(years(valid), station_tmp(valid), 1);
        raw_p = polyfit(years(valid), raw_tmp(valid), 1);
        bc_p = polyfit(years(valid), bc_tmp(valid), 1);

        % Store trends (units per year)
        station_trends(i_station) = station_p(1);
        raw_trends(i_station) = raw_p(1);
        bc_trends(i_station) = bc_p(1);

    end

end

end