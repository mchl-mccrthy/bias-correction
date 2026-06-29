function [station_clim_var_yearly, raw_clim_var_station_yearly, ...
    bc_clim_var_station_yearly, years] = makeyearlytables( ...
    station_clim_var, raw_clim_var_station, bc_clim_var_station, ...
    raw_time, agg_method)

% Make yearly aggregated versions of station, raw, and bias-corrected tables

% Get years in study period
years = unique(year(raw_time));
n_years = numel(years);
n_stations = width(station_clim_var);

% Preallocate yearly tables
station_clim_var_yearly = array2table(nan(n_years,n_stations), ...
    'VariableNames', station_clim_var.Properties.VariableNames);

raw_clim_var_station_yearly = array2table(nan(n_years,n_stations), ...
    'VariableNames', raw_clim_var_station.Properties.VariableNames);

bc_clim_var_station_yearly = array2table(nan(n_years,n_stations), ...
    'VariableNames', bc_clim_var_station.Properties.VariableNames);

% Loop through years and stations
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

            else
                error('agg_method must be ''sum'' or ''mean''.')
            end
        end
    end
end

end