% Plot map

% Add path to third party functions
addpath(genpath('third_party'))

%% Specify variable
var_name = 'tas';
nc_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\StLucia_1981_2020\tas_bc_StLucia_1981_2020.nc';
units = '\circC';
var_name_long = 'Temperature';

shp_path = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\cordex_data\gadm41_ARM_shp\gadm41_ARM_0.shp';

start_yr = 2004;
end_yr = 2020;

cmap_name = 'RdBu';
flip_cmap = true;
cmap_lims = [-2 2];
proc = 'trend'; % 'mean'
n_levels = 100;

fig_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\StLucia_1981_2020\figures\pr_bc_StLucia_1981_2020_trend.png';

stn_coord_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\StLucia\proc_data\StLucia_coordinates.csv';
stn_data_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\StLucia\proc_data\StLucia_tas.csv';

% unit_conversion = @(x) x; % Precipitation (mm year^{-1})
unit_conversion = @(x) x*10; % Temperature trend (°C decade^-1)
% unit_conversion = @(x) x-273.15; % Temperature (\circC)

%% Load grid data
var = ncread(nc_path,var_name);
latitude = ncread(nc_path,'lat');
longitude = ncread(nc_path,'lon');

% Permute
var = permute(var,[2 1 3]);

%% Convert daily grid data to annual
time = ncread(nc_path,'time');
time_units = ncreadatt(nc_path,'time','units');

ref_date = datetime(extractAfter(time_units,'since '));
dates = ref_date + days(time);

years = year(dates);
uy = unique(years);
ny = length(uy);

[nlat,nlon,~] = size(var);
var_year = nan(nlat,nlon,ny);

for i = 1:ny

    ind = years == uy(i);

    if strcmp(var_name,'pr')
        var_year(:,:,i) = sum(var(:,:,ind),3);
    else
        var_year(:,:,i) = mean(var(:,:,ind),3);
    end

end

var = var_year;

var(:,:,uy < start_yr | uy > end_yr) = [];

%% Load shapefile
shp = shaperead(shp_path);

%% Create mask
[lon_grid,lat_grid] = meshgrid(longitude,latitude);
mask = inpolygons(lon_grid,lat_grid,shp.X,shp.Y);

%% Load station coordinates
stns = readtable(stn_coord_path);

%% Load station data
stn_data = readtable(stn_data_path);

dates = datetime(stn_data.year,stn_data.month,stn_data.day);

years = year(dates);
uy = unique(years);
ny = length(uy);

nstn = width(stn_data) - 3;

stn_year = nan(ny,nstn);

%% Aggregate daily station data to annual
for i = 1:ny

    ind = years == uy(i);

    data = stn_data{ind,4:end};

    % fraction of valid daily observations
    valid_frac = sum(~isnan(data),1) ./ size(data,1);

    if strcmp(var_name,'pr')
        stn_year(i,:) = nansum(data,1);
    else
        stn_year(i,:) = nanmean(data,1);
    end

    % discard years with insufficient coverage
    stn_year(i,valid_frac < 0.8) = NaN;

end

stn_year(uy < start_yr | uy > end_yr,:) = [];

%% Process grid data
if strcmp(proc,'mean')

    var_proc = mean(var,3);
    var_proc = unit_conversion(var_proc);

elseif strcmp(proc,'trend')

    [nlat,nlon,nt] = size(var);

    var2 = reshape(var,[],nt)';

    t = (1:nt)';
    X = [ones(nt,1) t];

    beta = X\var2;

    var_proc = reshape(beta(2,:),nlat,nlon);

    var_proc = unit_conversion(var_proc);

end

%% Process station data
stn_proc = nan(1,nstn);

if strcmp(proc,'mean')

    stn_proc = nanmean(stn_year,1);

elseif strcmp(proc,'trend')

    for s = 1:nstn

        y = stn_year(:,s);

        ind = ~isnan(y);

        if sum(ind) > 5

            t = (1:sum(ind))';
            X = [ones(sum(ind),1) t];

            beta = X \ y(ind);

            stn_proc(s) = beta(2);

        end

    end

end

stn_proc = unit_conversion(stn_proc);

%% Aspect ratio correction
lat_range = max(latitude)-min(latitude);
ll_ratio = 1./cosd(mean(lat_range));

%% Mask outside Armenia
var_proc(~mask) = NaN;

%% Plot
figure()

contourf(longitude,latitude,var_proc,...
    linspace(cmap_lims(1),cmap_lims(2),n_levels),...
    'LineColor','none')

cmap = brewermap(n_levels,cmap_name);

if flip_cmap
    cmap = flipud(cmap);
end

colormap(cmap)

c = colorbar;
c.Label.String = [var_name_long ' (' units ')'];

caxis([cmap_lims(1) cmap_lims(2)])

hold on

% Country outline
plot(shp.X,shp.Y,'k')

% Plot stations (only valid ones)
valid = ~isnan(stn_proc);

scatter(stns.lon(valid),stns.lat(valid),70,stn_proc(valid),...
    'filled','MarkerEdgeColor','k','LineWidth',0.8)

xlabel('Longitude (\circ)')
ylabel('Latitude (\circ)')

axis off

formatfigure(gcf,5,5/ll_ratio,2)

print(gcf,fig_path,'-dpng','-r300')