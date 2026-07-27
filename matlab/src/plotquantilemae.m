% Make strip plot of quantile mean absolute errors
function plotquantilemae(raw_quantile_mae,bc_quantile_mae,file_path_figures,...
    clim_var_name,clim_var_long_name,clim_var_units)

% Make plot
figure()
hold on
plotstripgroup(raw_quantile_mae,1,[0.45 0.45 0.45]);
plotstripgroup(bc_quantile_mae,2,'r')
yticks([1 2])
yticklabels({'Raw','Bias-corrected'})
ylim([0.5 2.5])
xlabel(['MAE, ' lower(clim_var_long_name) ' quantiles (' clim_var_units ')'])
formatfigure(gcf,4,2,4)
print(gcf,fullfile(file_path_figures,[clim_var_name ...
    '_quantile_mae_strip.png']),'-dpng','-r300');

end

% Plot one deterministic jittered strip group
function plotstripgroup(values,y_value,color_value)

% Keep finite values
values = values(isfinite(values));
values = values(:)';
n_values = numel(values);
if n_values == 0
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
scatter(values,y_values,'filled',...
    'MarkerFaceColor',color_value,'MarkerEdgeColor',color_value)
hold on
plot([median(values,'omitnan') median(values,'omitnan')],...
    [y_value-0.18 y_value+0.18],'k','LineWidth',1)

end
