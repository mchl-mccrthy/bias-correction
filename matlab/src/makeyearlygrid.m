% Make grid data yearly
function [grid_clim_var_yearly,years] = makeyearlygrid(grid_clim_var,grid_time,agg_method)

% Get years
years = unique(year(grid_time));

% Get sizes
n_years = numel(years);
n_rows = size(grid_clim_var,1);
n_cols = size(grid_clim_var,2);

% Preallocate space for yearly data
grid_clim_var_yearly = nan(n_rows,n_cols,n_years,class(grid_clim_var));

% Loop through years aggregating
for i_year = 1:n_years
    ind_year = year(grid_time) == years(i_year);
    if strcmp(agg_method,'sum')
        grid_clim_var_yearly(:,:,i_year) = ...
            sum(grid_clim_var(:,:,ind_year),3,'omitnan');
    elseif strcmp(agg_method,'mean')
        grid_clim_var_yearly(:,:,i_year) = ...
            mean(grid_clim_var(:,:,ind_year),3,'omitnan');
    end
end

end