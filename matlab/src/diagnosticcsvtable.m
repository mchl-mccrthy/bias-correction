% Add plain-text units for CSV export without changing internal metric names.
function out = diagnosticcsvtable(input,cfg)
out = input;
native = plainunits(formatunits(cfg.clim_var_units));
yearly = plainunits(yearlyunits(cfg.clim_var_units,cfg.agg_method));
trend = plainunits(trendunits(cfg.clim_var_units,cfg.agg_method));
names = out.Properties.VariableNames;
for i = 1:numel(names)
    name = names{i};
    if ismember(name,{'Variable','Station','Dataset'})
        continue
    elseif strcmp(name,'MAE_quantiles')
        units = native;
    elseif contains(name,'trend')
        units = trend;
    else
        units = yearly;
    end
    names{i} = [strrep(name,'_',' ') ' (' units ')'];
end
out.Properties.VariableNames = names;
end

function units = plainunits(units)
units = strrep(units,'\circC',[char(176) 'C']);
units = erase(units,{'$','{','}'});
end
