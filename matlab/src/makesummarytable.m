% Make table of summary diagnostics
function summary_table = makesummarytable(clim_var_name,station_trends,...
    raw_station_trends,bc_station_trends,raw_quantile_mae,...
    bc_quantile_mae,raw_annual_mae,bc_annual_mae,...
    station_means,raw_station_means,bc_station_means)

% Make table rows
variable = {clim_var_name; clim_var_name};
dataset = {'Raw'; 'Bias-corrected'};
mae_quantiles = [mean(raw_quantile_mae,'omitnan'); ...
    mean(bc_quantile_mae,'omitnan')];
mae_annual = [mean(raw_annual_mae,'omitnan'); ...
    mean(bc_annual_mae,'omitnan')];
mae_linear_trends = [trendmae(station_trends,raw_station_trends); ...
    trendmae(station_trends,bc_station_trends)];

% Assemble table
summary_table = table(variable,dataset,mae_quantiles,mae_annual,...
    mae_linear_trends,...
    'VariableNames',{'Variable','Dataset','MAE_quantiles','MAE_yearly',...
    'MAE_linear_trends'});
summary_table.Observed_mean = repmat(mean(station_means,'omitnan'),2,1);
summary_table.Model_mean = [mean(raw_station_means,'omitnan'); ...
    mean(bc_station_means,'omitnan')];
summary_table.Observed_linear_trend = repmat(mean(station_trends,'omitnan'),2,1);
summary_table.Model_linear_trend = [mean(raw_station_trends,'omitnan'); ...
    mean(bc_station_trends,'omitnan')];

end

% Calculate MAE between station and gridded trends at station locations
function mae = trendmae(station_trends,model_trends)

% Keep finite values
valid = isfinite(station_trends) & isfinite(model_trends);

% Calculate MAE
if ~any(valid)
    mae = NaN;
else
    mae = mean(abs(model_trends(valid)-station_trends(valid)),'omitnan');
end

end
