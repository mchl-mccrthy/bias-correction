% Make yearly aggregated versions of station, raw, and bias-corrected tables
function [station_clim_var_yearly,raw_station_clim_var_yearly,...
    bc_station_clim_var_yearly,years] = makeyearlytables( ...
    station_clim_var,raw_station_clim_var,bc_station_clim_var,...
    raw_time,agg_method)

% Specify how much of a year needs to be there for yearly values to be
% computed
min_year_completeness = 0.90;

% Get years in study period
years = unique(year(raw_time));
n_years = numel(years);
n_stations = width(station_clim_var);

% Preallocate yearly tables
station_clim_var_yearly = array2table(nan(n_years,n_stations),...
    'VariableNames',station_clim_var.Properties.VariableNames);
raw_station_clim_var_yearly = array2table(nan(n_years,n_stations),...
    'VariableNames',raw_station_clim_var.Properties.VariableNames);
bc_station_clim_var_yearly = array2table(nan(n_years,n_stations),...
    'VariableNames',bc_station_clim_var.Properties.VariableNames);

% Loop through years and stations
for i_year = 1:n_years
    ind_year = year(raw_time) == years(i_year);
    for i_station = 1:n_stations
        station_tmp = station_clim_var{ind_year,i_station};
        completeness = sum(~isnan(station_tmp)) / numel(station_tmp);
        if completeness >= min_year_completeness
            if strcmp(agg_method,'sum')
                station_clim_var_yearly{i_year,i_station} = ...
                    sum(station_clim_var{ind_year,i_station},'omitnan');
                raw_station_clim_var_yearly{i_year,i_station} = ...
                    sum(raw_station_clim_var{ind_year,i_station},'omitnan');
                bc_station_clim_var_yearly{i_year,i_station} = ...
                    sum(bc_station_clim_var{ind_year,i_station},'omitnan');
            elseif strcmp(agg_method,'mean')
                station_clim_var_yearly{i_year,i_station} = ...
                    mean(station_clim_var{ind_year,i_station},'omitnan');
                raw_station_clim_var_yearly{i_year,i_station} = ...
                    mean(raw_station_clim_var{ind_year,i_station},'omitnan');
                bc_station_clim_var_yearly{i_year,i_station} = ...
                    mean(bc_station_clim_var{ind_year,i_station},'omitnan');
            end
        end
    end
end

end