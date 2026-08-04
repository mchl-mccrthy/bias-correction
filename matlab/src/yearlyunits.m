% Get units for yearly diagnostic values
function units_yearly = yearlyunits(clim_var_units,agg_method)

% Mean aggregation keeps the native units
if strcmp(agg_method,'mean')
    units_yearly = formatunits(clim_var_units);
    return
end

% Sum aggregation removes a terminal inverse timestep before annualising
base_units = stripterminalinversetimestep(clim_var_units);
base_units = formatunits(base_units);
units_yearly = appendunitfactor(base_units,'year^{-1}');

end
