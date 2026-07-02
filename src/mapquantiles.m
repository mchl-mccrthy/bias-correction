function [bc_grid_clim_var,grid_biases] = mapquantiles(raw_grid_clim_var,station_lon,station_lat,...
    qmfs,raw_lon,raw_lat,bc_type,qmf_period,raw_time)

% Get quantiles
station_quantiles = real(qmfs);
raw_quantiles = imag(qmfs);

% Get biases
if strcmp(bc_type,'multiplicative')

    % Wrt precipitation, inf occurs if observation is more than zero and
    % raw gridded is zero, which rarely happens in reality (e.g. McCarthy 
    % et al (2022) Supplementary Information, Figure S4). NaN occurs when 
    % both observation and raw gridded are zero, in which case multiplying
    % the raw gridded by zero is appropriate.  
    biases = station_quantiles./raw_quantiles;
    biases(isnan(biases) | isinf(biases)) = 0;
elseif strcmp(bc_type,'additive')
    biases = station_quantiles-raw_quantiles;
end

% Get size of downscaled raw gridded variable
n_rows = size(raw_grid_clim_var,1);
n_cols = size(raw_grid_clim_var,2);
n_timesteps = size(raw_grid_clim_var,3);

% Preallocate space for downscaled, bias-corrected gridded variable
bc_grid_clim_var = nan(n_rows,n_cols,n_timesteps,'single');
if nargout > 1
    grid_biases = nan(n_rows,n_cols,n_timesteps,'single');
end

% Precompute grid-station distances once***
grid_x = raw_lon(:);
grid_y = raw_lat(:);
D_all = sqrt((grid_x - station_lon(:)').^2 + ...
             (grid_y - station_lat(:)').^2);
D_all(D_all == 0) = eps;  % avoid division by zero

% Precompute nearest grid cell for each station
[station_rows,station_cols] = indexofclosest2( ...
    station_lon, station_lat, raw_lon, raw_lat);
station_lin_inds = sub2ind(size(raw_lon),station_rows,station_cols);

% Loop through time steps
for i_timestep = 1:n_timesteps
    
    % Get downscaled raw gridded variable for timestep
    raw_grid_clim_var_timestep = raw_grid_clim_var(:,:,i_timestep);
    
    % Interpolate to station locations
    n_stations = length(station_lon);
    raw_station_clim_var_timestep = raw_grid_clim_var_timestep(station_lin_inds);
    
    % Make condition for qmf period
    if strcmp(qmf_period,'whole')
        i_period = 1;
    elseif strcmp(qmf_period,'seasonal')
        i_period = season(raw_time(i_timestep));
    elseif strcmp(qmf_period,'monthly')
        i_period = month(raw_time(i_timestep));
    end

    % Get biases for those stations. Here it does not matter if biases are
    % multiplicative or additive
    station_biases_timestep = nan(1,n_stations);
    for i_station = 1:n_stations
        if sum(~isnan(raw_quantiles(:,i_station,i_period))) > 0
            [~,quantile_index] = min(abs(raw_station_clim_var_timestep(i_station)-...
                squeeze(raw_quantiles(:,i_station,i_period))),...
                [],1,'includenan');
            station_biases_timestep(i_station) = biases(quantile_index,i_station,i_period);
        end
    end
    
    % Interpolate biases to grid  
    valid = isfinite(station_biases_timestep);
    D = D_all(:,valid);
    b = station_biases_timestep(valid);
    W = D.^-2;
    W = W ./ sum(W,2);
    grid_biases_timestep = W * b(:);
    grid_biases_timestep = reshape(grid_biases_timestep,size(raw_lon));
    
    % In case interpolation introduced sub-zero values, which shouldn't
    % happen
    if strcmp(bc_type,'multiplicative')
        grid_biases_timestep(grid_biases_timestep < 0) = 0;
    end

    % Apply biases to get downscaled, bias-corrected
    % gridded variable for timestep
    if strcmp(bc_type,'multiplicative') 
        bc_grid_clim_var_timestep = grid_biases_timestep.*raw_grid_clim_var_timestep;
    elseif strcmp(bc_type,'additive')
        bc_grid_clim_var_timestep = grid_biases_timestep+raw_grid_clim_var_timestep;
    end

    % Put timestep back in array
    bc_grid_clim_var(:,:,i_timestep) = bc_grid_clim_var_timestep;
    if nargout > 1
        grid_biases(:,:,i_timestep) = single(grid_biases_timestep);
    end
end

end