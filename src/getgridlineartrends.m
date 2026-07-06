function grid_linear_trends = getgridlineartrends(grid_clim_var_yearly,years)

n_rows = size(grid_clim_var_yearly,1);
n_cols = size(grid_clim_var_yearly,2);

grid_linear_trends = nan(n_rows,n_cols);

for i_row = 1:n_rows
    for i_col = 1:n_cols
        grid_tmp = squeeze(grid_clim_var_yearly(i_row,i_col,:));
        valid = ~isnan(grid_tmp);

        if sum(valid) >= 2
            p = polyfit(years(valid),grid_tmp(valid),1);
            grid_linear_trends(i_row,i_col) = p(1);
        end
    end
end

end