% Get Theil-Sen slopes from yearly climate data
function [station_slopes,raw_slopes,bc_slopes] = gettheilsenslopes(...
    station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years)

n_stations = width(station_clim_var_yearly);
station_slopes = nan(1,n_stations);
raw_slopes = nan(1,n_stations);
bc_slopes = nan(1,n_stations);

for i_station = 1:n_stations
    station_tmp = station_clim_var_yearly{:,i_station};
    raw_tmp = raw_station_clim_var_yearly{:,i_station};
    bc_tmp = bc_station_clim_var_yearly{:,i_station};
    valid = isfinite(station_tmp) & isfinite(raw_tmp) & isfinite(bc_tmp);
    if sum(valid) >= 2
        station_slopes(i_station) = ...
            theilsenslope(years(valid),station_tmp(valid));
        raw_slopes(i_station) = ...
            theilsenslope(years(valid),raw_tmp(valid));
        bc_slopes(i_station) = ...
            theilsenslope(years(valid),bc_tmp(valid));
    end
end

end
