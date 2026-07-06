% Get quantile mapping functions at stations
function qmfs = getqmfs(station_clim_var,station_coords,station_time,...
    raw_clim_var,raw_lon,raw_lat,raw_time,qmf_period,n_quantiles)

% Get periods
if strcmp(qmf_period,'whole')
    periods = 1;
elseif strcmp(qmf_period,'seasonal')
    periods = 1:4;
elseif strcmp(qmf_period,'monthly')
    periods = 1:12;
else
    error('qmf_period must be ''whole'', ''seasonal'', or ''monthly''.')
end

% Get dimensions
n_stations = height(station_coords);
n_periods = length(periods);

% Preallocate
qmfs.probabilities = linspace(0,1,n_quantiles);
qmfs.station_quantiles = nan(n_quantiles,n_stations,n_periods);
qmfs.raw_quantiles = nan(n_quantiles,n_stations,n_periods);

% Loop through stations
for i_station = 1:n_stations

    % Get station data
    station_clim_var_tmp = station_clim_var{:,i_station};
    station_lat_tmp = station_coords.lat(i_station);
    station_lon_tmp = station_coords.lon(i_station);

    % Get raw climate data at station location
    [row,col] = indexofclosest2(station_lon_tmp,station_lat_tmp, ...
        raw_lon,raw_lat);
    raw_station_clim_var = squeeze(raw_clim_var(row,col,:));

    % Loop through periods
    for i_period = 1:n_periods
        if strcmp(qmf_period,'whole')
            cond_station = true(size(station_time));
            cond_raw = true(size(raw_time));
        elseif strcmp(qmf_period,'seasonal')
            cond_station = season(station_time) == periods(i_period);
            cond_raw = season(raw_time) == periods(i_period);
        elseif strcmp(qmf_period,'monthly')
            cond_station = month(station_time) == periods(i_period);
            cond_raw = month(raw_time) == periods(i_period);
        end
        qmf = getqmf( ...
            station_time(cond_station), ...
            station_clim_var_tmp(cond_station), ...
            raw_time(cond_raw), ...
            raw_station_clim_var(cond_raw),n_quantiles);
        qmfs.station_quantiles(:,i_station,i_period) = qmf.station_quantiles;
        qmfs.raw_quantiles(:,i_station,i_period) = qmf.raw_quantiles;
    end
end

end