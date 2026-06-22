% Plot map

% Add path to third party functions
addpath(genpath('third_party'))

% Specify variable
var_name = 'tas';
nc_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\StLucia_1981_2020\tas_bc_StLucia_1981_2020.nc';
units = '\circC decade^{-1}';
var_name_long = 'Temperature trend';
shp_path = 'N:\gebhyd\8_Him\Personal_folders\Mike\foracca\cordex_data\gadm41_ARM_shp\gadm41_ARM_0.shp';
cmap_name = 'RdBu';
flip_cmap = true;
cmap_lims = [-0.8 0.8];
proc = 'trend'; % 'mean', 
n_levels = 100;
fig_path = 'C:\Users\McCarthy\Desktop\bias_correction\output_data\StLucia_1981_2020\figures\tas_bc_StLucia_1981_2020_trend.png';
stn_path = 'C:\Users\McCarthy\Desktop\bias_correction\input_data\station_data\StLucia\proc_data\StLucia_coordinates.csv';
% unit_conversion = @(x) x; % Precipitation (mm year^{-1})
% unit_conversion = @(x) x-273.15; % Temperature (\circC)
% unit_conversion = @(x) x*10; % Precipitation trend (mm decade^{-1})
unit_conversion = @(x) x*10; % Temperature trend (\circC decade^{-1})

% Load .nc file
var = ncread(nc_path,var_name);
latitude = ncread(nc_path,'lat');
longitude = ncread(nc_path,'lon');

% Permute
var = permute(var,[2 1 3]);

% Convert daily data to annual values
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
        var_year(:,:,i) = sum(var(:,:,ind),3); % annual precipitation
    else
        var_year(:,:,i) = mean(var(:,:,ind),3); % annual temperature
    end
end
var = var_year;

% Load shapefile
shp = shaperead(shp_path);

% Get mask
[lon_grid,lat_grid] = meshgrid(longitude,latitude);
mask = inpolygons(lon_grid,lat_grid,shp.X,shp.Y);

% Load station locations
stns = readtable(stn_path);

% Process data
if strcmp(proc,'mean')
    var_proc = mean(var,3);
    var_proc = unit_conversion(var_proc);
elseif strcmp(proc,'trend')
    [nlat,nlon,nt] = size(var);
    var = reshape(var,[],nt)';
    t = (1:nt)';
    X = [ones(nt,1) t];
    beta = X\var;
    var_proc = reshape(beta(2,:),nlat,nlon);
    var_proc = unit_conversion(var_proc);
end

% Get lat, lon ratio
lat_range = max(latitude)-min(latitude);
ll_ratio = 1./cosd(mean(lat_range));

% Mask areas outside shapefile
var_proc(~mask) = NaN;

% Plot
figure()
contourf(longitude,latitude,var_proc,linspace(cmap_lims(1),cmap_lims(2),n_levels),'LineColor','none')
cmap = brewermap(n_levels,cmap_name);
if flip_cmap
    cmap = flipud(cmap);
end
colormap(cmap);
c = colorbar;
c.Label.String = [var_name_long ' (' units ')'];
caxis([cmap_lims(1) cmap_lims(2)])
hold on
plot(shp.X,shp.Y,'k')
scatter(stns.lon,stns.lat,'k.')
xlabel('Longitude (\circ)')
ylabel('Latitude (\circ)')
axis off
formatfigure(gcf,5,5/ll_ratio,2)
print(gcf,fig_path,'-dpng','-r300')