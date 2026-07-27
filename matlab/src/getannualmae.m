% Get station-level mean absolute error from yearly climate data
function [raw_annual_mae,bc_annual_mae] = getannualmae(...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly)

% Get number of stations
n_stations = width(station_clim_var_yearly);

% Preallocate space for annual MAE
raw_annual_mae = nan(1,n_stations);
bc_annual_mae = nan(1,n_stations);

% Loop through stations
for i_station = 1:n_stations

    % Extract annual values
    station_tmp = station_clim_var_yearly{:,i_station};
    raw_tmp = raw_station_clim_var_yearly{:,i_station};
    bc_tmp = bc_station_clim_var_yearly{:,i_station};

    % Keep only years where all three datasets are available
    valid = ~isnan(station_tmp) & ...
            ~isnan(raw_tmp) & ...
            ~isnan(bc_tmp);

    % Calculate MAE if any valid years are available
    if any(valid)
        raw_annual_mae(i_station) = mean(abs(raw_tmp(valid) - station_tmp(valid)),...
            'omitnan');
        bc_annual_mae(i_station) = mean(abs(bc_tmp(valid) - station_tmp(valid)),...
            'omitnan');
    end
end

end
