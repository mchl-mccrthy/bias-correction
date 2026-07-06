function grid_trends_out = interptrends(station_trends, station_x, station_y, grid_x, grid_y, grid_trends, bc_type, idw_power)

nt = size(station_trends,1);
nx = size(grid_x,1);
ny = size(grid_x,2);
n_stns = length(station_x);

grid_trends_out = zeros(nx,ny,nt);

[rows,cols] = indexofclosest2(station_x,station_y,grid_x,grid_y);

grid_at_stations = nan(1,n_stns);

grid_x_vec = grid_x(:);
grid_y_vec = grid_y(:);
D_all = sqrt((grid_x_vec - station_x(:)').^2 + ...
             (grid_y_vec - station_y(:)').^2);
D_all(D_all == 0) = eps;

for t = 1:nt
    
    for i_stn = 1:n_stns
        grid_at_stations(i_stn) = grid_trends(rows(i_stn),cols(i_stn),t);
    end

    stn_vals = station_trends(t,:);

    if strcmp(bc_type,'additive')
        corr_vals = stn_vals - grid_at_stations;
        corr_vals(~isfinite(corr_vals)) = 0;
    else
        corr_vals = stn_vals ./ grid_at_stations;
        corr_vals(~isfinite(corr_vals)) = 1;
    end

    valid = isfinite(corr_vals);
    D = D_all(:,valid);
    b = corr_vals(valid);
    W = D.^-idw_power;
    W = W ./ sum(W,2);
    corr_grid = W * b(:);
    corr_grid = reshape(corr_grid,size(grid_x));

    if strcmp(bc_type,'additive')
        grid_trends_out(:,:,t) = grid_trends(:,:,t) + corr_grid;
    else
        grid_trends_out(:,:,t) = grid_trends(:,:,t) .* corr_grid;
    end

end

grid_trends_out = single(grid_trends_out);

end