% Get quantile mapping function
function qmf = getqmf(station_clim_var,raw_clim_var,n_quantiles)

% Get climate values
station_values = station_clim_var;
raw_values = raw_clim_var;

% Remove NaNs from both datasets (although there should be none in the 
% gridded)
make_nan = isnan(raw_values) | isnan(station_values);
raw_values(make_nan) = NaN;
station_values(make_nan) = NaN;

% Specify quantiles
qs = linspace(0,1,n_quantiles);

% Get quantiles
qmf.probabilities = qs;
qmf.station_quantiles = quantile(station_values,qs);
qmf.raw_quantiles = quantile(raw_values,qs);

end
