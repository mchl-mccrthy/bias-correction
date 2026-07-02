% Get quantile mapping function
function qmf = getqmf(station_time,station_clim_var,raw_time,raw_clim_var)

% Make tables
station_data = table(station_time,station_clim_var);
raw_data = table(raw_time,raw_clim_var);

% Retime station data to gridded data
raw_data = table2timetable(raw_data);
station_data = table2timetable(station_data);
station_data = retime(station_data,raw_data.raw_time);

% Get variable data from tables
station_values = station_data.station_clim_var;
raw_values = raw_data.raw_clim_var;

% Remove NaNs from both datasets (although there should be none in the 
% gridded)
make_nan = isnan(raw_values) | isnan(station_values);
raw_values(make_nan) = NaN;
station_values(make_nan) = NaN;

% Specify number of quantiles
nQs = 1001;
qs = linspace(0,1,nQs);

% Get quantiles
station_quantiles = quantile(station_values,qs);
raw_quantiles = quantile(raw_values,qs);

% Get mapping function
qmf = complex(station_quantiles,raw_quantiles);

end
