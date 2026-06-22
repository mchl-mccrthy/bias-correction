%% Plot map of sum or mean over a selected date range
% Memory-safe version: reads only selected NetCDF time slices

% Add path to third party functions
addpath(genpath('third_party'))

%% User settings
var_name = 'tasmin';
nc_path = '\\wsl.localhost\Ubuntu\home\mccarthy\projects\climate_indices\output_data\tropical_nights.nc';

units = 'days';
var_name_long = 'Tropical nights';

shp_path = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\cordex_data\gadm41_ARM_shp\gadm41_ARM_0.shp';

stn_coord_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_coordinates.csv';
stn_data_path  = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_tasmax.csv';

plot_stations = false;

date_start = datetime(1981,1,1);
date_end   = datetime(2020,12,31);

% 'sum' for precipitation, 'mean' for temperature
proc = 'mean';

cmap_name = 'Reds';
flip_cmap = false;
cmap_lims = [0 35];
n_levels = 100;

use_log_cscale = false;
log_offset = 0.1;
log_ticks = [0 10 20 50 100 200 500 1000];

fig_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\Armenia_1981_2020\figures\tropical_nights_1981_2020.png';

unit_conversion = @(x) x;
% unit_conversion = @(x) x;
% unit_conversion = @(x) x - 273.15;

min_valid_frac = 0.8;

title_text = '1981-2020';

%% Load grid metadata only

latitude = ncread(nc_path, 'lat');
longitude = ncread(nc_path, 'lon');

nlat = numel(latitude);
nlon = numel(longitude);

%% Load time and select requested period

time = ncread(nc_path, 'time');
time_units = ncreadatt(nc_path, 'time', 'units');

ref_date = datetime(extractAfter(time_units, 'since '));
dates = ref_date + days(time);

time_idx = find(dates >= date_start & dates <= date_end);

if isempty(time_idx)
    error('No grid data found within the selected date range.')
end

%% Aggregate grid data over selected period, memory-safe

var_accum   = zeros(nlat, nlon, 'single');
valid_accum = zeros(nlat, nlon, 'single');

for tt = 1:numel(time_idx)

    % Assumes NetCDF variable order is [lon lat time]
    tmp = ncread(nc_path, var_name, ...
        [1 1 time_idx(tt)], ...
        [Inf Inf 1]);

    % Convert [lon lat] to [lat lon]
    tmp = single(permute(tmp, [2 1]));

    valid = ~isnan(tmp);
    tmp(~valid) = 0;

    var_accum = var_accum + tmp;
    valid_accum = valid_accum + single(valid);

    clear tmp valid

end

switch lower(proc)
    case 'sum'
        var_proc = var_accum;
        var_proc(valid_accum == 0) = NaN;

    case 'mean'
        var_proc = var_accum ./ valid_accum;
        var_proc(valid_accum == 0) = NaN;

    otherwise
        error('proc must be ''sum'' or ''mean''.')
end

var_proc = unit_conversion(var_proc);

clear var_accum valid_accum

%% Load shapefile

shp = shaperead(shp_path);

%% Create mask

[lon_grid, lat_grid] = meshgrid(longitude, latitude);
mask = inpolygons(lon_grid, lat_grid, shp.X, shp.Y);

clear lon_grid lat_grid

%% Load and process station data, if requested

if plot_stations

    stns = readtable(stn_coord_path);
    stn_data = readtable(stn_data_path);

    stn_dates = datetime(stn_data.year, stn_data.month, stn_data.day);
    stn_mask = stn_dates >= date_start & stn_dates <= date_end;

    if ~any(stn_mask)
        warning('No station data found within the selected date range. Stations will not be plotted.')
        plot_stations = false;

    else
        data_sel = stn_data{stn_mask, 4:end};
        nstn = size(data_sel, 2);

        valid_frac = sum(~isnan(data_sel), 1) ./ size(data_sel, 1);

        switch lower(proc)
            case 'sum'
                stn_proc = sum(data_sel, 1, 'omitnan');

            case 'mean'
                stn_proc = mean(data_sel, 1, 'omitnan');

            otherwise
                error('proc must be ''sum'' or ''mean''.')
        end

        stn_proc(valid_frac < min_valid_frac) = NaN;
        stn_proc = unit_conversion(stn_proc);
    end

end

%% Aspect ratio correction

lat_range = max(latitude)-min(latitude);
ll_ratio = 1./cosd(mean(lat_range));

%% Mask outside polygon

var_proc(~mask) = NaN;

clear mask

%% Prepare colour-scale data

plot_var = var_proc;

plot_var(plot_var < cmap_lims(1)) = cmap_lims(1);
plot_var(plot_var > cmap_lims(2)) = cmap_lims(2);

if use_log_cscale
    plot_var = log10(plot_var + log_offset);
    plot_lims = log10(cmap_lims + log_offset);
    plot_levels = log10(linspace(cmap_lims(1), cmap_lims(2), n_levels) + log_offset);
else
    plot_lims = cmap_lims;
    plot_levels = linspace(cmap_lims(1), cmap_lims(2), n_levels);
end

%% Plot

figure()

contourf(longitude, latitude, plot_var, ...
    plot_levels, ...
    'LineColor', 'none')

cmap = brewermap(n_levels, cmap_name);

if flip_cmap
    cmap = flipud(cmap);
end

colormap(cmap)

c = colorbar;
c.Label.String = [var_name_long ' (' units ')'];

if use_log_cscale
    c.Ticks = log10(log_ticks + log_offset);
    c.TickLabels = string(log_ticks);
end

caxis(plot_lims)

hold on

plot(shp.X, shp.Y, 'k')

if plot_stations
    valid = ~isnan(stn_proc);

    stn_plot = stn_proc;
    stn_plot(stn_plot < cmap_lims(1)) = cmap_lims(1);
    stn_plot(stn_plot > cmap_lims(2)) = cmap_lims(2);

    if use_log_cscale
        stn_plot = log10(stn_plot + log_offset);
    end

    scatter(stns.lon(valid), stns.lat(valid), 70, stn_plot(valid), ...
        'filled', 'MarkerEdgeColor', 'k', 'LineWidth', 0.8)
end

title(title_text)

xlabel('Longitude (\circ)')
ylabel('Latitude (\circ)')

axis off

formatfigure(gcf, 5, 5/ll_ratio, 2)

print(gcf, fig_path, '-dpng', '-r300')