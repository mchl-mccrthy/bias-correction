% Get station-level mean absolute error from climate-data quantiles
function [raw_quantile_mae,bc_quantile_mae] = getquantilemae(...
    station_clim_var,raw_station_clim_var,bc_station_clim_var)

% Get number of stations
n_stations = width(station_clim_var);

% Preallocate space for quantile MAE
raw_quantile_mae = nan(1,n_stations);
bc_quantile_mae = nan(1,n_stations);
q = linspace(0,1,1000);

% Loop through stations
for i_station = 1:n_stations

    % Extract timestep values
    station_tmp = station_clim_var{:,i_station};
    raw_tmp = raw_station_clim_var{:,i_station};
    bc_tmp = bc_station_clim_var{:,i_station};

    % Keep only timesteps where all three datasets are available
    valid = ~isnan(station_tmp) & ...
            ~isnan(raw_tmp) & ...
            ~isnan(bc_tmp);

    % Calculate MAE between empirical quantiles
    if any(valid)
        station_quantiles = quantile(station_tmp(valid),q);
        raw_quantiles = quantile(raw_tmp(valid),q);
        bc_quantiles = quantile(bc_tmp(valid),q);
        raw_quantile_mae(i_station) = mean(...
            abs(raw_quantiles - station_quantiles),'omitnan');
        bc_quantile_mae(i_station) = mean(...
            abs(bc_quantiles - station_quantiles),'omitnan');
    end
end

end
