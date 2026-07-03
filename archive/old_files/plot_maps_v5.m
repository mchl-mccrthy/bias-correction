%% Plot map of seasonal climate anomalies relative to climatology
% Memory-safe version: reads one NetCDF time slice at a time

% Add path to third party functions
addpath(genpath('third_party'))

%% User settings

var_name = 'pr';
nc_path = '\\wsl.localhost\Ubuntu\home\mccarthy\projects\climate_indices\input_data\pr_bc_Armenia_1981_2020.nc';

units = 'mm';
var_name_long = 'Summer precipitation anomaly';

shp_path = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\cordex_data\gadm41_ARM_shp\gadm41_ARM_0.shp';

stn_coord_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_coordinates.csv';
stn_data_path  = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_pr.csv';

plot_stations = true;

target_year = 2000;
clim_years = 1981:2020;

season_months = [6 7 8];   % JJA summer

% 'sum' for precipitation, 'mean' for temperature
proc = 'sum';

% 'difference' or 'percent'
anom_mode = 'percent';

cmap_name = 'BrBG';
flip_cmap = false;
cmap_lims = [-100 100];
n_levels = 100;

use_log_cscale = false;
log_offset = 0.1;
log_ticks = [0 10 20 50 100 200 500 1000];

fig_path = sprintf('C:\\Users\\McCarthy\\Desktop\\bias_correction\\output_data\\Armenia_1981_2020\\figures\\summer_%d_pr_anomaly.png', target_year);

% Unit conversion
unit_conversion = @(x) x;          % precipitation already in desired units
% unit_conversion = @(x) x - 273.15;   % temperature in K to degC

min_valid_frac = 0.8;

title_text = sprintf('Summer %d anomaly relative to %d-%d', ...
    target_year, min(clim_years), max(clim_years));

%% Load grid metadata only

latitude = ncread(nc_path, 'lat');
longitude = ncread(nc_path, 'lon');

nlat = numel(latitude);
nlon = numel(longitude);

%% Load time

time = ncread(nc_path, 'time');
time_units = ncreadatt(nc_path, 'time', 'units');

ref_date = datetime(extractAfter(time_units, 'since '));
dates = ref_date + days(time);

yr = year(dates);
mo = month(dates);

%% Calculate seasonal climatology and target year, memory-safe

years_unique = clim_years(:);
nyears = numel(years_unique);

if ~ismember(target_year, years_unique)
    error('target_year is not included in clim_years.')
end

% Online climatology accumulators
var_clim_sum = zeros(nlat, nlon, 'single');
var_clim_n   = zeros(nlat, nlon, 'single');

% Target year field
var_target = NaN(nlat, nlon, 'single');

for ii = 1:nyears

    this_year = years_unique(ii);
    this_time_idx = find(yr == this_year & ismember(mo, season_months));

    if isempty(this_time_idx)
        warning('No grid data found for year %d.', this_year)
        continue
    end

    % Accumulators for this year only
    var_accum   = zeros(nlat, nlon, 'single');
    valid_accum = zeros(nlat, nlon, 'single');

    for tt = 1:numel(this_time_idx)

        % Assumes NetCDF variable order is [lon lat time]
        tmp = ncread(nc_path, var_name, ...
            [1 1 this_time_idx(tt)], ...
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
            var_year = var_accum;
            var_year(valid_accum == 0) = NaN;

        case 'mean'
            var_year = var_accum ./ valid_accum;
            var_year(valid_accum == 0) = NaN;

        otherwise
            error('proc must be ''sum'' or ''mean''.')
    end

    % Save target year
    if this_year == target_year
        var_target = var_year;
    end

    % Add this yearly seasonal value to climatology
    valid_year = ~isnan(var_year);
    tmp_year = var_year;
    tmp_year(~valid_year) = 0;

    var_clim_sum = var_clim_sum + tmp_year;
    var_clim_n   = var_clim_n + single(valid_year);

    clear var_accum valid_accum var_year valid_year tmp_year

end

var_clim = var_clim_sum ./ var_clim_n;
var_clim(var_clim_n == 0) = NaN;

clear var_clim_sum var_clim_n

%% Calculate grid anomaly

var_target = unit_conversion(var_target);
var_clim   = unit_conversion(var_clim);

switch lower(anom_mode)
    case 'difference'
        var_proc = var_target - var_clim;

    case 'percent'
        var_proc = 100 * (var_target - var_clim) ./ var_clim;
        var_proc(var_clim == 0) = NaN;

    otherwise
        error('anom_mode must be ''difference'' or ''percent''.')
end

clear var_target var_clim

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
    stn_yr = year(stn_dates);
    stn_mo = month(stn_dates);

    data_all = stn_data{:, 4:end};
    nstn = size(data_all, 2);

    stn_yearly = NaN(nyears, nstn);

    for ii = 1:nyears

        this_mask = stn_yr == years_unique(ii) & ismember(stn_mo, season_months);

        if ~any(this_mask)
            warning('No station data found for year %d.', years_unique(ii))
            continue
        end

        data_sel = data_all(this_mask, :);

        valid_frac = sum(~isnan(data_sel), 1) ./ size(data_sel, 1);

        switch lower(proc)
            case 'sum'
                tmp = sum(data_sel, 1, 'omitnan');

            case 'mean'
                tmp = mean(data_sel, 1, 'omitnan');

            otherwise
                error('proc must be ''sum'' or ''mean''.')
        end

        tmp(valid_frac < min_valid_frac) = NaN;

        stn_yearly(ii,:) = tmp;

    end

    target_idx = years_unique == target_year;

    stn_target = stn_yearly(target_idx,:);
    stn_clim = mean(stn_yearly, 1, 'omitnan');

    stn_target = unit_conversion(stn_target);
    stn_clim   = unit_conversion(stn_clim);

    switch lower(anom_mode)
        case 'difference'
            stn_proc = stn_target - stn_clim;

        case 'percent'
            stn_proc = 100 * (stn_target - stn_clim) ./ stn_clim;
            stn_proc(stn_clim == 0) = NaN;
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

switch lower(anom_mode)
    case 'difference'
        c.Label.String = [var_name_long ' (' units ')'];

    case 'percent'
        c.Label.String = [var_name_long ' (%)'];
end

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