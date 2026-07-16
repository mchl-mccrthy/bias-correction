% Get quantile mapping functions at stations
function qmfs = getqmfs(station_clim_var,station_x,station_y,station_time,...
    raw_clim_var,raw_x,raw_y,raw_time,qmf_period,n_quantiles)

% Check station time and raw time match
if ~isequal(station_time(:),raw_time(:))
    error('Station and grid time vectors must match exactly.')
end

% Get periods
if strcmp(qmf_period,'whole')
    periods = 1;
elseif strcmp(qmf_period,'seasonal')
    periods = 1:4;
elseif strcmp(qmf_period,'monthly')
    periods = 1:12;
end

% Get dimensions
n_stations = numel(station_x);
n_periods = length(periods);

% Preallocate space for quantiles and probabilities
qmfs.probabilities = linspace(0,1,n_quantiles);
qmfs.station_quantiles = nan(n_quantiles,n_stations,n_periods);
qmfs.raw_quantiles = nan(n_quantiles,n_stations,n_periods);

% Loop through stations
for i_station = 1:n_stations

    % Get station data
    station_clim_var_tmp = station_clim_var{:,i_station};
    station_x_tmp = station_x(i_station);
    station_y_tmp = station_y(i_station);

    % Get raw climate data at station location
    [row,col] = indexofclosest2(station_x_tmp,station_y_tmp, ...
        raw_x,raw_y);
    raw_station_clim_var = squeeze(raw_clim_var(row,col,:));

    % Loop through periods
    for i_period = 1:n_periods
        if strcmp(qmf_period,'whole')
            cond = true(size(raw_time));
        elseif strcmp(qmf_period,'seasonal')
            cond = season(raw_time) == periods(i_period);
        elseif strcmp(qmf_period,'monthly')
            cond = month(raw_time) == periods(i_period);
        end

        % Get quantile mapping functions
        qmf = getqmf( ...
            station_clim_var_tmp(cond), ...
            raw_station_clim_var(cond), ...
            n_quantiles);
        qmfs.station_quantiles(:,i_station,i_period) = qmf.station_quantiles;
        qmfs.raw_quantiles(:,i_station,i_period) = qmf.raw_quantiles;
    end
end

end