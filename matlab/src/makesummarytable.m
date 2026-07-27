% Make table of summary diagnostics
function summary_table = makesummarytable(clim_var_name,station_trends,...
    raw_station_trends,bc_station_trends,raw_quantile_mae,...
    bc_quantile_mae,raw_annual_mae,bc_annual_mae)

% Make table rows
variable = {clim_var_name; clim_var_name};
dataset = {'Raw'; 'Bias-corrected'};
mae_quantiles = [mean(raw_quantile_mae,'omitnan'); ...
    mean(bc_quantile_mae,'omitnan')];
mae_annual = [mean(raw_annual_mae,'omitnan'); ...
    mean(bc_annual_mae,'omitnan')];
r2_trends = [trendr2(station_trends,raw_station_trends); ...
    trendr2(station_trends,bc_station_trends)];

% Assemble table
summary_table = table(variable,dataset,mae_quantiles,mae_annual,r2_trends,...
    'VariableNames',{'Variable','Dataset','MAE_quantiles','MAE_annual',...
    'r2_trends'});

end

% Calculate r2 between station and gridded trends at station locations
function r2 = trendr2(station_trends,model_trends)

% Keep finite values
valid = isfinite(station_trends) & isfinite(model_trends);

% Calculate r2
if sum(valid) < 2
    r2 = NaN;
else
    r = corr(station_trends(valid)',model_trends(valid)');
    r2 = r^2;
end

end
