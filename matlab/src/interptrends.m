function grid_trends_out = interptrends(station_trends,station_x,...
    station_y,station_z,grid_x,grid_y,grid_z,grid_trends,bc_type,...
    idw_power,coordinate_system,idw_method,idw_alpha)

% Get sizes
n_timesteps = size(station_trends,1);
n_cols = size(grid_x,1);
n_rows = size(grid_x,2);
n_stations = length(station_x);

% Preallocate space for trends
grid_trends_out = zeros(n_cols,n_rows,n_timesteps);

% Get closest grid cell to each station
[rows,cols] = indexofclosest2(station_x,station_y,grid_x,grid_y);

% Preallocatte space for grid values at stations
grid_at_stations = nan(1,n_stations);

% Precompute distances for IDW
D_all = getdistances(grid_x(:),grid_y(:),station_x,station_y,...
    coordinate_system,grid_z(:),station_z,idw_method,idw_alpha);

% Loop through time steps
for i_timestep = 1:n_timesteps
    
    % Loop through stations
    for i_station = 1:n_stations
        grid_at_stations(i_station) = grid_trends(rows(i_station),...
            cols(i_station),i_timestep);
    end

    % Get station values
    stn_vals = station_trends(i_timestep,:);

    % If station trend corrections are unavailable, use a neutral 
    % correction so the raw gridded trend is retained
    if strcmp(bc_type,'additive')
        corr_vals = stn_vals - grid_at_stations;
        corr_vals(~isfinite(corr_vals)) = 0;
    else
        corr_vals = stn_vals ./ grid_at_stations;
        corr_vals(~isfinite(corr_vals)) = 1;
    end

    % Do IDW interp
    valid = isfinite(corr_vals);
    D = D_all(:,valid);
    b = corr_vals(valid);
    W = D.^-idw_power;
    W = W./sum(W,2);
    corr_grid = W*b(:);
    corr_grid = reshape(corr_grid,size(grid_x));

    % Correct trends
    if strcmp(bc_type,'additive')
        grid_trends_out(:,:,i_timestep) = ...
            grid_trends(:,:,i_timestep)+corr_grid;
    else
        grid_trends_out(:,:,i_timestep) = ...
            grid_trends(:,:,i_timestep).*corr_grid;
    end

end

end