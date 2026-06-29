% Bias correct climate data

% Notes
% - Raw climate data need to be stored in a particular way. The dimensions
%   of the climate variable must be: lon, lat, time. This is the standard
%   used by ECMWF.
% - Note that this assumes station data are in same time zone as gridded
%   climate data.
% - Station data should also cover the same time period as the gridded
%   data, without any missing days. NaNs are allowed though.

%% Initiate workflow

% Display progress
disp('Bias correcting climate data')

% Specify some variables
clim_var_name = 'pr';
clim_var_long_name = 'Precipitation';
clim_var_units = 'mm';
qmf_period = 'monthly'; % 'whole','seasonal', or 'monthly'
bias_interp_method = 'idw'; 
bc_type = 'multiplicative';
preserve_trends = 'yes'; % Preserve station trends?
trend_window = 365*5; % days
agg_method = 'sum'; % For yearly aggregations, 'sum' or 'mean'

% Specify file paths
file_path_station_coords = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\stations\StLucia_coordinates.csv';
file_path_station_clim_var = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\interim\stations\StLucia_pr.csv';
file_path_raw_data = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\raw\chelsa\pr_StLucia_1981_2020.nc';
file_path_bc_data = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\processed\key_variables\reanalysis\pr_bc_StLucia_1981_2020.nc';
file_path_figures = '\\wsl.localhost\Ubuntu\home\mccarthy\storage\mccarthy\climate_pipeline\StLucia\temp\';

% Add paths 
addpath(genpath('src'))

%% Load climate variable at station and coordinates
[station_clim_var,station_coords,station_lat,station_lon,station_time,...
    n_stations] = loadstationdata(file_path_station_clim_var,...
    file_path_station_coords);

%% Load raw climate data and format
[raw_clim_var,raw_lon,raw_lat,raw_time] = loadrawdata(file_path_raw_data,...
    clim_var_name);

%% Retime station to gridded data with NaNs
if strcmp(preserve_trends,'yes')
    T = table2timetable(station_clim_var,'RowTimes',station_time);
    T = retime(T,raw_time);
    T = timetable2table(T);
    station_time = T.Time;
    station_clim_var = removevars(T,'Time');
    clearvars T
end

%% Get trends
if strcmp(preserve_trends,'yes')
    grid_trends = get_trends(raw_clim_var,3,trend_window);
    station_trends = get_trends(station_clim_var{:,:},1,trend_window);
end

%% Detrend
if strcmp(preserve_trends,'yes')
    raw_clim_var = detrend(raw_clim_var,grid_trends,bc_type);
    station_clim_var{:,:} = detrend(station_clim_var{:,:},station_trends,...
        bc_type);
end

%% Loop through stations and periods getting quantiles

% Specify number of periods 
if strcmp(qmf_period,'whole')
    periods = 1;
elseif strcmp(qmf_period,'seasonal')
    periods = 1:4;
elseif strcmp(qmf_period,'monthly')
    periods = 1:12;
end

% Loop through stations getting station and raw climate data
n_time_steps = length(raw_time);
n_periods = length(periods);
qmfs = nan(1001,n_stations,n_periods);
raw_clim_var_at_station = nan(n_time_steps,1);
for i_station = 1:n_stations

    % Load station data
    station_clim_var_tmp = station_clim_var.(i_station);
    station_lat_tmp = station_coords.lat(i_station);
    station_lon_tmp = station_coords.lon(i_station);
    
    % Get raw climate data at station locations
    [row,col] = indexofclosest2(station_lon_tmp,station_lat_tmp,raw_lon,...
        raw_lat);
    raw_clim_var_at_station = squeeze(raw_clim_var(row,col,:));
    
    % Get quantile mapping functions
    for i_period = 1:n_periods
        if strcmp(qmf_period,'whole')
            cond_station = ones(size(station_time));
            cond_raw = ones(size(raw_time));
        elseif strcmp(qmf_period,'seasonal')
            cond_station = season(station_time) == periods(i_period);
            cond_raw = season(raw_time) == periods(i_period);
        elseif strcmp(qmf_period,'monthly')
            cond_station = month(station_time) == periods(i_period);
            cond_raw = month(raw_time) == periods(i_period);
        end
        qmfs(:,i_station,i_period) = getqmf(station_time(cond_station),...
            station_clim_var_tmp(cond_station),...
            raw_time(cond_raw),raw_clim_var_at_station(cond_raw));
    end
end

%% Correct reanalysis
bc_clim_var = mapquantiles(raw_clim_var,station_lon,...
    station_lat,qmfs,raw_lon,raw_lat,bias_interp_method,bc_type,...
    qmf_period,raw_time);

%% Interpolate station trends to grid
if strcmp(preserve_trends,'yes')  
    grid_trends_interp = interpolate_trends( ...
        station_trends, ...
        station_coords.lon, station_coords.lat, ...
        raw_lon, raw_lat, ...
        grid_trends,bc_type);
    grid_trends_interp = single(grid_trends_interp);
end

%% Clear raw data to avoid OOM
clear raw_clim_var grid_trends

%% Retrend 
if strcmp(preserve_trends,'yes')
    bc_clim_var = retrend(bc_clim_var,grid_trends_interp,bc_type);
    station_clim_var{:,:} = retrend(station_clim_var{:,:},station_trends,bc_type);
end

%% Clear interpolated grid trends and reload raw data
clear grid_trends_interp
[raw_clim_var,~,~,~] = loadrawdata(file_path_raw_data,clim_var_name);

%% Get raw and bias-corrected climate variables at stations
raw_clim_var_station = extract_grid_at_stations( ...
    raw_clim_var, station_lon, station_lat, raw_lon, raw_lat, station_clim_var);
bc_clim_var_station = extract_grid_at_stations( ...
    bc_clim_var, station_lon, station_lat, raw_lon, raw_lat, station_clim_var);

%% Make yearly versions of those tables

% Get years in study period
years = unique(year(raw_time));
n_years = numel(years);

% Preallocate space for yearly data
station_clim_var_yearly = array2table(nan(n_years,n_stations), ...
    'VariableNames', station_clim_var.Properties.VariableNames);
raw_clim_var_station_yearly = array2table(nan(n_years,n_stations), ...
    'VariableNames', raw_clim_var_station.Properties.VariableNames);
bc_clim_var_station_yearly = array2table(nan(n_years,n_stations), ...
    'VariableNames', bc_clim_var_station.Properties.VariableNames);

% Get yearly data from daily
for i_year = 1:n_years
    ind_year = year(raw_time) == years(i_year);
    for i_station = 1:n_stations
        station_tmp = station_clim_var{ind_year,i_station};
        completeness = sum(~isnan(station_tmp)) / numel(station_tmp);
        if completeness >= 0.90
            if strcmp(agg_method,'sum')
                station_clim_var_yearly{i_year,i_station} = ...
                    sum(station_clim_var{ind_year,i_station},'omitnan');
                raw_clim_var_station_yearly{i_year,i_station} = ...
                    sum(raw_clim_var_station{ind_year,i_station},'omitnan');
                bc_clim_var_station_yearly{i_year,i_station} = ...
                    sum(bc_clim_var_station{ind_year,i_station},'omitnan');
            elseif strcmp(agg_method,'mean')
                station_clim_var_yearly{i_year,i_station} = ...
                    mean(station_clim_var{ind_year,i_station},'omitnan');
                raw_clim_var_station_yearly{i_year,i_station} = ...
                    mean(raw_clim_var_station{ind_year,i_station},'omitnan');
                bc_clim_var_station_yearly{i_year,i_station} = ...
                    mean(bc_clim_var_station{ind_year,i_station},'omitnan');
            end
        end
    end
end

%% Get linear trends

% Preallocate
bc_trends = nan(1,n_stations);
station_trends = nan(1,n_stations);
raw_trends = nan(1,n_stations);

% Loop through stations
for i_station = 1:n_stations

    % Which years are non-NaN?
    valid = ~isnan(bc_clim_var_station_yearly{:,i_station}) & ~isnan(station_clim_var_yearly{:,i_station}) & ~isnan(raw_clim_var_station_yearly{:,i_station});
    bc_tmp = bc_clim_var_station_yearly{:,i_station};
    stn_tmp = station_clim_var_yearly{:,i_station};
    raw_tmp = raw_clim_var_station_yearly{:,i_station};
    bc_tmp = bc_tmp(valid);
    stn_tmp = stn_tmp(valid);
    raw_tmp = raw_tmp(valid);

    % Fit linear regression
    bc_p = polyfit(years(valid),bc_tmp,1);
    station_p = polyfit(years(valid),stn_tmp,1);
    raw_p = polyfit(years(valid),raw_tmp,1);

    % Get trends (per year)
    bc_trends(i_station) = bc_p(1);
    station_trends(i_station) = station_p(1);
    raw_trends(i_station) = raw_p(1);
end

%% Make plots

% Plot stations
figure()
for i_station = 1:n_stations
    scatter(station_time,...
        station_clim_var{:,i_station}./station_clim_var...
        {:,i_station}*i_station,'blue'); hold on
    text(station_time(end)+calyears(1),i_station,...
        station_coords.station{i_station},'Interpreter','none',...
        'FontSize',7)
end
xlim([station_time(1) station_time(end)])
ylim([0 n_stations+1])
yticklabels([])
formatfigure(gcf,5,3,4)
print(gcf,[file_path_figures '/' clim_var_name '_station_availability.png'],...
    '-dpng','-r300');

% Plot trends
figure()
scatter(station_trends,raw_trends); hold on
scatter(station_trends,bc_trends)
xlabel([clim_var_long_name ' trend, stations (' clim_var_units ' year^{-1})'])
ylabel([clim_var_long_name ' trend, gridded (' clim_var_units ' year^{-1})'])
xlim([min([station_trends bc_trends raw_trends 0]) max([station_trends bc_trends raw_trends 0])])
ylim([min([station_trends bc_trends raw_trends 0]) max([station_trends bc_trends raw_trends 0])])
legend('Raw','Bias corrected','Location','eastoutside')
formatfigure(gcf,4,4,4)

% Plot histograms and quantile plots of overlapping time periods
for i_station = 1:n_stations
    
    % Plot time series
    figure()
    plot(raw_time,squeeze(raw_clim_var_station{:,i_station}),'g'); hold on
    plot(raw_time,squeeze(bc_clim_var_station{:,i_station}),'b'); hold on
    plot(station_time,station_clim_var{:,i_station},'r')
    ylabel([clim_var_long_name ' (' clim_var_units ')'])
    xlim([min(raw_time) max(raw_time)])
    title(station_coords.station{i_station})
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,7,2,4)
    print(gcf,[file_path_figures '/' station_coords.station{i_station}...
        '_' clim_var_name '_time_series.png'],'-dpng','-r300');

    % Plot histograms
    figure()
    raw_clim_var_tmp = squeeze(raw_clim_var_station{:,i_station});
    bc_clim_var_tmp = squeeze(bc_clim_var_station{:,i_station});
    station_clim_var_tmp = station_clim_var{:,i_station};
    [common_time,ia,ib] = intersect(raw_time,station_time);
    raw_clim_var_overlap = raw_clim_var_tmp(ia);
    bc_clim_var_overlap = bc_clim_var_tmp(ia);
    station_clim_var_overlap = station_clim_var_tmp(ib);
    time_overlap = common_time;
    valid = ~isnan(raw_clim_var_overlap) & ...
        ~isnan(bc_clim_var_overlap) & ...
        ~isnan(station_clim_var_overlap);
    raw_clim_var_overlap = raw_clim_var_overlap(valid);
    bc_clim_var_overlap = bc_clim_var_overlap(valid);
    station_clim_var_overlap = station_clim_var_overlap(valid);
    hold on
    hist_max = max([max(raw_clim_var_overlap) max(bc_clim_var_overlap) max(station_clim_var_overlap)]);
    hist_min = min([min(raw_clim_var_overlap) min(bc_clim_var_overlap) min(station_clim_var_overlap)]);
    histogram(raw_clim_var_overlap,linspace(hist_min,hist_max,25))
    histogram(bc_clim_var_overlap,linspace(hist_min,hist_max,25))
    histogram(station_clim_var_overlap,linspace(hist_min,hist_max,25))
    ylabel('Count ()')
    xlabel([clim_var_long_name ' (' clim_var_units ')'])
    title(station_coords.station{i_station})
    if contains(clim_var_name,'pr')
        xlim([0 50])
    end
    xlim([hist_min hist_max])
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,4,4,4)
    print(gcf,[file_path_figures '/' station_coords.station{i_station}...
        '_' clim_var_name '_histogram.png'],'-dpng','-r300');

    % Make quantile-quantile plots
    figure()
    hold on
    q = linspace(0,1,1000);
    station_quantiles = quantile(station_clim_var_overlap, q);
    raw_quantiles = quantile(raw_clim_var_overlap, q);
    bc_quantiles = quantile(bc_clim_var_overlap, q);
    plot(station_quantiles,raw_quantiles,'r')
    plot(station_quantiles,bc_quantiles,'b')
    grid on
    ylabel([clim_var_long_name ',' newline ...
        'raw and bias corrected (' clim_var_units ')'])
    xlabel([clim_var_long_name ', station (' clim_var_units ')'])
    title(station_coords.station{i_station})
    xlim([hist_min hist_max])
    ylim([hist_min hist_max])
    if contains(clim_var_name,'pr')
        xlim([0 50])
        ylim([0 50])
    end
    legend('Raw','Bias corrected','Location','eastoutside')
    formatfigure(gcf,4,4,4)
    print(gcf,[file_path_figures '/' station_coords.station{i_station}...
        '_' clim_var_name '_quantile-quantile.png'],'-dpng','-r300');

    % Make yearly time series
    figure()
    plot(years,raw_clim_var_station_yearly{:,i_station},'g'); hold on
    plot(years,bc_clim_var_station_yearly{:,i_station},'b'); hold on
    plot(years,station_clim_var_yearly{:,i_station},'r')
    ylabel([clim_var_long_name ' (' clim_var_units ')'])
    xlim([min(years) max(years)])
    title(station_coords.station{i_station})
    legend('Raw','Bias corrected','Station','Location','eastoutside')
    formatfigure(gcf,7,2,4)
    print(gcf,[file_path_figures '/' station_coords.station{i_station}...
        '_' clim_var_name '_time_series_yearly.png'],'-dpng','-r300');

end

% Make map of bias corrected data
figure()
contourf(raw_lon,raw_lat,mean(bc_clim_var,3),100,'LineColor','none')
c = colorbar;
c.Label.String = [clim_var_long_name ' (' clim_var_units ')'];
title('Long-term average');
ll_ratio = (max(raw_lon,[],'all')-min(raw_lon,[],'all'))./(max(raw_lat,...
    [],'all')-min(raw_lat,[],'all'));
formatfigure(gcf,4,4/ll_ratio,2)
print(gcf,[file_path_figures '/' clim_var_name '_long-term_average.png'],...
    '-dpng','-r300');

%% Permute back to ECMWF standard
bc_clim_var = permute(bc_clim_var,[2 1 3]);

%% Put bias corrected data in netcdf file

% Copy file and write new data
%copyfile(file_path_raw_data,file_path_bc_data);
%ncwrite(file_path_bc_data,clim_var_name,bc_clim_var);

% Update documentation
%ncwriteatt(file_path_bc_data,clim_var_name,'bias_correction',...
%    'empirical quantile mapping');
%ncwriteatt(file_path_bc_data,'/','history', ...
%    sprintf('%s: replaced %s with bias-corrected data (EQM)',...
%    datestr(now,30),clim_var_name));
