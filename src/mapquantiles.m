function [bc_clim_var,grid_biases] = mapquantiles(raw_clim_var,station_lon,station_lat,...
    qmfs,raw_lon,raw_lat,bias_interp_method,bc_type,qmf_period,raw_time)

% Get quantiles
varAwsQ = real(qmfs);
varReaQ = imag(qmfs);

% Get biases
if strcmp(bc_type,'multiplicative')

    % Wrt precipitation, inf occurs if observation is more than zero and
    % reanalysis is zero, which rarely happens in reality (e.g. McCarthy 
    % et al (2022) Supplementary Information, Figure S4). NaN occurs when 
    % both observation and reanalysis are zero, in which case multiplying
    % the reanalysis by zero is appropriate.  
    biases = varAwsQ./varReaQ;
    biases(isnan(biases) | isinf(biases)) = 0;
elseif strcmp(bc_type,'additive')
    biases = varAwsQ-varReaQ;
end

% Get size of downscaled reanalysis variable
nRows = size(raw_clim_var,1);
nCols = size(raw_clim_var,2);
nTimesteps = size(raw_clim_var,3);

% Preallocate space for downscaled, bias-corrected reanalysis variable
bc_clim_var = nan(nRows,nCols,nTimesteps,'single');
grid_biases = nan(nRows,nCols,nTimesteps,'single');

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
for iTimestep = 1:nTimesteps
    
    % Get downscaled reanalysis variable for timestep
    reaVarTs = raw_clim_var(:,:,iTimestep);
    
    % Interpolate to station locations
    nStns = length(station_lon);
    reaVarStnTs = reaVarTs(station_lin_inds);
    
    % Make condition for qmf period
    if strcmp(qmf_period,'whole')
        iPrd = 1;
    elseif strcmp(qmf_period,'seasonal')
        iPrd = season(raw_time(iTimestep));
    elseif strcmp(qmf_period,'monthly')
        iPrd = month(raw_time(iTimestep));
    end

    % Get biases for those stations. Here it does not matter if biases are
    % multiplicative or additive
    stnBiasesTs = nan(1,nStns);
    for iStn = 1:nStns
        if sum(~isnan(varReaQ(:,iStn,iPrd))) > 0
            [~,indQ] = min(abs(reaVarStnTs(iStn)-...
                squeeze(varReaQ(:,iStn,iPrd))),...
                [],1,'includenan');
            stnBiasesTs(iStn) = biases(indQ,iStn,iPrd);
        end
    end
    
    % Interpolate biases to grid  
    if strcmp(bias_interp_method,'nearest')
        [stnX2,stnY2,stnBiasesTs2] = prepsd(station_lon,station_lat,...
            stnBiasesTs);
        surfFunBiases = fit([stnX2,stnY2],stnBiasesTs2,'nearest');
        gridBiasesTs = surfFunBiases(raw_lon,raw_lat);
        gridBiasesTs = reshape(gridBiasesTs,size(raw_lon));
    elseif strcmp(bias_interp_method,'tpaps')
        stnXys = rot90([station_lon(:),station_lat(:)]);
        demXys = rot90([raw_lon(:),raw_lat(:)]);
        fnSplineStn = tpaps(stnXys,stnBiasesTs);
        gridBiasesTs = fnval(fnSplineStn,demXys);
        gridBiasesTs = gridBiasesTs(:);
        gridBiasesTs = reshape(gridBiasesTs,size(raw_lon));
    elseif strcmp(bias_interp_method,'idw')
        valid = isfinite(stnBiasesTs);
        D = D_all(:,valid);
        b = stnBiasesTs(valid);
        W = D.^-2;
        W = W ./ sum(W,2);
        gridBiasesTs = W * b(:);
        gridBiasesTs = reshape(gridBiasesTs,size(raw_lon));
    end
    
    % In case interpolation introduced sub-zero values, which shouldn't
    % happen
    if strcmp(bc_type,'multiplicative')
        gridBiasesTs(gridBiasesTs < 0) = 0;
    end

    % Apply biases to get downscaled, bias-corrected
    % reanalysis variable for timestep
    if strcmp(bc_type,'multiplicative') 
        bcReaVarTs = gridBiasesTs.*reaVarTs;
    elseif strcmp(bc_type,'additive')
        bcReaVarTs = gridBiasesTs+reaVarTs;
    end

    % Put timestep back in array
    bc_clim_var(:,:,iTimestep) = bcReaVarTs;
    grid_biases(:,:,iTimestep) = gridBiasesTs;
end

end