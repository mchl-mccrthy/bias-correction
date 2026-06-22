%% Make GIF map from daily nc data: one day per frame

addpath(genpath('third_party'))

%% User settings
var_name = 'tas';
nc_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\Armenia_1981_2020\tas_bc_Armenia_1981_2020.nc';

units = '\circC';
var_name_long = 'Temperature';

shp_path = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\cordex_data\gadm41_ARM_shp\gadm41_ARM_0.shp';

stn_coord_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_coordinates.csv';
stn_data_path  = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\Armenia\proc_data\Armenia_tas.csv';

plot_stations = false;

% Year to animate
plot_year = 2020;
date_start = datetime(plot_year,1,1);
date_end   = datetime(plot_year,12,31);

cmap_name = 'RdBu';
flip_cmap = true;

% Colour scale limits in original precipitation units
cmap_lims = [-30 30];
n_levels = 100;

% Nonlinear colour scale for precipitation
use_nonlinear_cscale = false;
precip_offset = 0.1;                 % avoids log10(0)
precip_ticks = [0 1 2 5 10 20 50 100];     % labels shown in original mm units

gif_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\Armenia_1981_2020\figures\tas_2020_daily.gif';

% GIF settings
delay_time = 0.15;
loop_count = Inf;

% Unit conversion
% unit_conversion = @(x) x;
unit_conversion = @(x) x-273.15; % degrees C

% Station settings
min_valid_frac = 0.8;

%% Load grid data
var = ncread(nc_path, var_name);
latitude = ncread(nc_path, 'lat');
longitude = ncread(nc_path, 'lon');

% Permute from [lon lat time] to [lat lon time]
var = permute(var, [2 1 3]);

%% Load time
time = ncread(nc_path, 'time');
time_units = ncreadatt(nc_path, 'time', 'units');

ref_date = datetime(extractAfter(time_units, 'since '));
dates = ref_date + days(time);

time_mask = dates >= date_start & dates <= date_end;

if ~any(time_mask)
    error('No grid data found within the selected year.')
end

var_sel = var(:,:,time_mask);
dates_sel = dates(time_mask);

%% Load shapefile and mask
shp = shaperead(shp_path);

[lon_grid, lat_grid] = meshgrid(longitude, latitude);
mask = inpolygons(lon_grid, lat_grid, shp.X, shp.Y);

%% Optional station data
if plot_stations
    stns = readtable(stn_coord_path);
    stn_data = readtable(stn_data_path);

    stn_dates = datetime(stn_data.year, stn_data.month, stn_data.day);
end

%% Aspect ratio correction
lat_range = max(latitude)-min(latitude);
ll_ratio = 1./cosd(mean(lat_range));

%% Colormap
cmap = brewermap(n_levels, cmap_name);

if flip_cmap
    cmap = flipud(cmap);
end

%% Define plotting levels
if use_nonlinear_cscale
    plot_lims = log10(cmap_lims + precip_offset);
    plot_levels = log10(linspace(cmap_lims(1), cmap_lims(2), n_levels) + precip_offset);
else
    plot_lims = cmap_lims;
    plot_levels = linspace(cmap_lims(1), cmap_lims(2), n_levels);
end

%% Create figure
fig = figure('Color', 'w');

for ii = 1:length(dates_sel)

    clf(fig)

    this_date = dates_sel(ii);

    %% Grid data for this day
    var_day = var_sel(:,:,ii);
    var_day = unit_conversion(var_day);
    var_day(~mask) = NaN;

    %% Clip to colour limits in original units
    plot_day = var_day;
    plot_day(plot_day < cmap_lims(1)) = cmap_lims(1);
    plot_day(plot_day > cmap_lims(2)) = cmap_lims(2);

    %% Apply nonlinear transform if requested
    if use_nonlinear_cscale
        plot_day = log10(plot_day + precip_offset);
    end

    %% Plot grid
    contourf(longitude, latitude, plot_day, plot_levels, ...
        'LineColor', 'none')

    colormap(cmap)
    caxis(plot_lims)

    c = colorbar;
    c.Label.String = [var_name_long ' (' units ')'];

    if use_nonlinear_cscale
        c.Ticks = log10(precip_ticks + precip_offset);
        c.TickLabels = string(precip_ticks);
    end

    hold on

    %% Country outline
    plot(shp.X, shp.Y, 'k')

    %% Optional station data for this day
    if plot_stations

        stn_mask = stn_dates == this_date;

        if any(stn_mask)
            data_day = stn_data{stn_mask, 4:end};

            valid_frac = sum(~isnan(data_day), 1) ./ size(data_day, 1);
            stn_day = mean(data_day, 1, 'omitnan');

            stn_day(valid_frac < min_valid_frac) = NaN;
            stn_day = unit_conversion(stn_day);

            % Clip station values in original units
            stn_day(stn_day < cmap_lims(1)) = cmap_lims(1);
            stn_day(stn_day > cmap_lims(2)) = cmap_lims(2);

            if use_nonlinear_cscale
                stn_plot = log10(stn_day + precip_offset);
            else
                stn_plot = stn_day;
            end

            valid = ~isnan(stn_plot);

            scatter(stns.lon(valid), stns.lat(valid), 70, stn_plot(valid), ...
                'filled', 'MarkerEdgeColor', 'k', 'LineWidth', 0.8)
        end
    end

    %% Labels and formatting
    title(sprintf('%s', datestr(this_date, 'yyyy-mm-dd')))

    xlabel('Longitude (\circ)')
    ylabel('Latitude (\circ)')

    axis off

    formatfigure(gcf, 5, 5/ll_ratio, 1.75)

    drawnow

    %% Capture frame and write GIF
    frame = getframe(fig);
    im = frame2im(frame);
    [A, map] = rgb2ind(im, 256);

    if ii == 1
        imwrite(A, map, gif_path, 'gif', ...
            'LoopCount', loop_count, ...
            'DelayTime', delay_time);
    else
        imwrite(A, map, gif_path, 'gif', ...
            'WriteMode', 'append', ...
            'DelayTime', delay_time);
    end

end

disp(['Saved GIF to: ' gif_path])