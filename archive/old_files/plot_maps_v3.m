%% Plot map of sum or mean over a selected date range

% Add path to third party functions
addpath(genpath('third_party'))

%% User settings
var_name = 'tas';
nc_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\Armenia_1981_2020\tas_bc_Armenia_1981_2020.nc';

units = '\circC';
var_name_long = 'Temperature';

shp_path = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\cordex_data\gadm41_ARM_shp\gadm41_ARM_0.shp';

stn_coord_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_coordinates.csv';
stn_data_path  = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_tas.csv';

% Select date range to aggregate over
date_start = datetime(2018,7,2);
date_end   = datetime(2018,7,2);

% Aggregation over the selected date range:
%   'sum'  -> e.g. precipitation
%   'mean' -> e.g. temperature
proc = 'mean';

cmap_name = 'RdBu';
flip_cmap = true;
cmap_lims = [0 42];   % adjust for your variable / date range
n_levels = 100;

fig_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\Armenia_1981_2020\figures\a.png';

% Unit conversion examples
% unit_conversion = @(x) x;          % Temperature already in °C
unit_conversion = @(x) x - 273.15; % If temperature is in K
% unit_conversion = @(x) x;          % Precipitation sum, etc.

% Minimum fraction of valid station observations in selected period
min_valid_frac = 0.8;

%% Load grid data
var = ncread(nc_path, var_name);
latitude = ncread(nc_path, 'lat');
longitude = ncread(nc_path, 'lon');

% Permute from [lon lat time] to [lat lon time] if needed
var = permute(var, [2 1 3]);

%% Load time and select requested period
time = ncread(nc_path, 'time');
time_units = ncreadatt(nc_path, 'time', 'units');

ref_date = datetime(extractAfter(time_units, 'since '));
dates = ref_date + days(time);

time_mask = dates >= date_start & dates <= date_end;

if ~any(time_mask)
    error('No grid data found within the selected date range.')
end

var_sel = var(:,:,time_mask);

%% Aggregate grid data over selected period
switch lower(proc)
    case 'sum'
        var_proc = sum(var_sel, 3, 'omitnan');
    case 'mean'
        var_proc = mean(var_sel, 3, 'omitnan');
    otherwise
        error('proc must be ''sum'' or ''mean''.')
end

var_proc = unit_conversion(var_proc);

%% Load shapefile
shp = shaperead(shp_path);

%% Create mask
[lon_grid, lat_grid] = meshgrid(longitude, latitude);
mask = inpolygons(lon_grid, lat_grid, shp.X, shp.Y);

%% Load station coordinates
stns = readtable(stn_coord_path);

%% Load station data
stn_data = readtable(stn_data_path);

stn_dates = datetime(stn_data.year, stn_data.month, stn_data.day);
stn_mask = stn_dates >= date_start & stn_dates <= date_end;

if ~any(stn_mask)
    error('No station data found within the selected date range.')
end

data_sel = stn_data{stn_mask, 4:end};   % station columns only
nstn = size(data_sel, 2);

% Fraction of valid observations at each station in selected period
valid_frac = sum(~isnan(data_sel), 1) ./ size(data_sel, 1);

stn_proc = nan(1, nstn);

switch lower(proc)
    case 'sum'
        stn_proc = sum(data_sel, 1, 'omitnan');
    case 'mean'
        stn_proc = mean(data_sel, 1, 'omitnan');
end

% Remove stations with insufficient coverage
stn_proc(valid_frac < min_valid_frac) = NaN;

stn_proc = unit_conversion(stn_proc);

%% Aspect ratio correction
lat_range = max(latitude)-min(latitude);
ll_ratio = 1./cosd(mean(lat_range));

%% Mask outside polygon
var_proc(~mask) = NaN;

%% Plot
figure()

contourf(longitude, latitude, var_proc, ...
    linspace(cmap_lims(1), cmap_lims(2), n_levels), ...
    'LineColor', 'none')

cmap = brewermap(n_levels, cmap_name);
if flip_cmap
    cmap = flipud(cmap);
end
colormap(cmap)

c = colorbar;
c.Label.String = [var_name_long ' (' units ')'];

caxis(cmap_lims)

hold on

% Country outline
plot(shp.X, shp.Y, 'k')

% Plot stations
valid = ~isnan(stn_proc);
scatter(stns.lon(valid), stns.lat(valid), 70, stn_proc(valid), ...
    'filled', 'MarkerEdgeColor', 'k', 'LineWidth', 0.8)

title(sprintf('%s %s from %s to %s', ...
    var_name_long, lower(proc), datestr(date_start, 'yyyy-mm-dd'), datestr(date_end, 'yyyy-mm-dd')))

xlabel('Longitude (\circ)')
ylabel('Latitude (\circ)')

axis off

formatfigure(gcf, 5, 5/ll_ratio, 2)

print(gcf, fig_path, '-dpng', '-r300')