% Mean and linear trend of the equal-cell yearly domain-average series.
function [domain_mean,domain_trend] = getdomainsummary(grid_yearly,years)
series = squeeze(mean(grid_yearly,[1 2],'omitnan'));
valid = isfinite(series);
domain_mean = mean(series(valid),'omitnan');
domain_trend = NaN;
if sum(valid) >= 2
    coefficients = polyfit(years(valid),series(valid),1);
    domain_trend = coefficients(1);
end
end
