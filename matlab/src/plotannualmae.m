% Make strip plot of annual mean absolute errors
function plotannualmae(raw_annual_mae,bc_annual_mae,file_path_figures_tables,...
    clim_var_name,clim_var_long_name,clim_var_units,agg_method)

% Get yearly units
annual_units = yearlyunits(clim_var_units,agg_method);
clim_var_long_name_lower = lower(clim_var_long_name);

% Make plot
figure()
hold on
h_raw = plotstripgroup(raw_annual_mae,1,[0.45 0.45 0.45]);
h_bc = plotstripgroup(bc_annual_mae,2,'r');
yticks([1 2])
yticklabels({'Raw','Bias-corrected'})
ylim([0.5 2.5])
xlabel(['MAE, yearly ' clim_var_long_name_lower ' (' annual_units ')'])
title('All stations, yearly MAE')
legend([h_raw h_bc],{'Raw','Bias-corrected'},'Location','eastoutside')
formatfigure(gcf,4,2,4)
print(gcf,fullfile(file_path_figures_tables,[clim_var_name ...
    '_annual_mae_strip.png']),'-dpng','-r300');

end

% Plot one deterministic jittered strip group
function h_scatter = plotstripgroup(values,y_value,color_value)

% Keep finite values
values = values(isfinite(values));
values = values(:)';
n_values = numel(values);
if n_values == 0
    h_scatter = gobjects(1);
    return
end

% Use deterministic vertical jitter
if n_values == 1
    jitter = 0;
else
    jitter = linspace(-0.12,0.12,n_values);
end

% Plot station values and group median
y_values = repmat(y_value,1,n_values) + jitter;
h_scatter = scatter(values,y_values,'filled',...
    'MarkerFaceColor',color_value,'MarkerEdgeColor',color_value);
hold on
plot([median(values,'omitnan') median(values,'omitnan')],...
    [y_value-0.18 y_value+0.18],'k','LineWidth',1)

end
