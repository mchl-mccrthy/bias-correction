% Mean and Theil-Sen slope of the yearly area-weighted domain-average series.
function [domain_mean,domain_slope] = getdomainsummary(...
    grid_yearly,years,grid_y,coordinate_system)
series = spatialmean(grid_yearly,grid_y,coordinate_system);
valid = isfinite(series);
domain_mean = mean(series(valid),'omitnan');
domain_slope = NaN;
if sum(valid) >= 2
    domain_slope = theilsenslope(years(valid),series(valid));
end
end
