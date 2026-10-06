% Get units for yearly Theil-Sen slope diagnostics
function units_trend = trendunits(clim_var_units,agg_method)

% Sum aggregation removes a terminal inverse timestep before trend units
if strcmp(agg_method,'sum')
    base_units = stripterminalinversetimestep(clim_var_units);
    base_units = formatunits(base_units);
    units_trend = appendunitfactor(base_units,'year^{-2}');
    return
end

% Mean aggregation keeps native units and adds per-year trend units
base_units = formatunits(clim_var_units);
units_trend = appendunitfactor(base_units,'year^{-1}');

end
