function [bcReaVar,gridBiases] = correctreanalysis_v3(reaVar,stnX,stnY,...
    stnZ,qmfs,reaX,reaY,reaZ,method,lapse,type,qmfPrd,bcReaDatetime)

% Get quantiles
varAwsQ = real(qmfs);
varReaQ = imag(qmfs);

% Get biases
if strcmp(type,'multiplicative')

    % Wrt precipitation, inf occurs if observation is more than zero and
    % reanalysis is zero, which rarely happens in reality (e.g. McCarthy 
    % et al (2022) Supplementary Information, Figure S4). NaN occurs when 
    % both observation and reanalysis are zero, in which case multiplying
    % the reanalysis by zero is appropriate.  
    biases = varAwsQ./varReaQ;
    biases(isnan(biases) | isinf(biases)) = 0;
elseif strcmp(type,'additive')
    biases = varAwsQ-varReaQ;
end

% Get size of downscaled reanalysis variable
nRows = size(reaVar,1);
nCols = size(reaVar,2);
nTimesteps = size(reaVar,3);

% Preallocate space for downscaled, bias-corrected reanalysis variable
bcReaVar = nan(nRows,nCols,nTimesteps);
gridBiases = nan(nRows,nCols,nTimesteps);

% Loop through time steps
for iTimestep = 1:nTimesteps
    
    % Get downscaled reanalysis variable for timestep
    reaVarTs = reaVar(:,:,iTimestep);
    
    % Interpolate to station locations
    nStns = length(stnX);
    if lapse == 1
        reaVarStnTs = nan(1,nStns);
        for iStn = 1:nStns
            Z = [ones(length(reaZ(:)),1) reaZ(:)];
            b = Z\reaVarTs(:);
            lr = b(2);
            reaVarStnTsInt = interp2(reaX,reaY,reaVarTs,stnX(iStn),...
                stnY(iStn),'linear');
            zInt = interp2(reaX,reaY,reaZ,stnX(iStn),stnY(iStn),'linear');
            reaVarStnTs(iStn) = reaVarStnTsInt+lr*(stnZ(iStn)-zInt);
        end
    else
    reaVarStnTs = interp2(reaX,reaY,reaVarTs,stnX,stnY,...
        'nearest');
    end
    
    % Make condition for qmf period
    if strcmp(qmfPrd,'whole')
        iPrd = 1;
    elseif strcmp(qmfPrd,'seasonal')
        iPrd = season(bcReaDatetime(iTimestep));
    elseif strcmp(qmfPrd,'monthly')
        iPrd = month(bcReaDatetime(iTimestep));
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
    if strcmp(method,'nearest')
        [stnX2,stnY2,stnBiasesTs2] = prepsd(stnX,stnY,...
            stnBiasesTs);
        surfFunBiases = fit([stnX2,stnY2],stnBiasesTs2,'nearest');
        gridBiasesTs = surfFunBiases(reaX,reaY);
        gridBiasesTs = reshape(gridBiasesTs,size(reaX));
    elseif strcmp(method,'tpaps')
        stnXys = rot90([stnX(:),stnY(:)]);
        demXys = rot90([reaX(:),reaY(:)]);
        fnSplineStn = tpaps(stnXys,stnBiasesTs);
        gridBiasesTs = fnval(fnSplineStn,demXys);
        gridBiasesTs = gridBiasesTs(:);
        gridBiasesTs = reshape(gridBiasesTs,size(reaX));
    elseif strcmp(method,'idw')
        [stnX2,stnY2,stnBiasesTs2] = prepsd(stnX,stnY,...
            stnBiasesTs);
        gridBiasesTs = IDW(stnX2,stnY2,stnBiasesTs2,reaX(1,:)',...
            reaY(:,1),-2,'ng',...
            length(stnX2));
    end
    
    % In case interpolation introduced sub-zero values, which shouldn't
    % happen
    if strcmp(type,'multiplicative')
        gridBiasesTs(gridBiasesTs < 0) = 0;
    end

    % Apply biases to get downscaled, bias-corrected
    % reanalysis variable for timestep
    if strcmp(type,'multiplicative') 
        bcReaVarTs = gridBiasesTs.*reaVarTs;
    elseif strcmp(type,'additive')
        bcReaVarTs = gridBiasesTs+reaVarTs;
    end

    % Put timestep back in array
    bcReaVar(:,:,iTimestep) = bcReaVarTs;
    gridBiases(:,:,iTimestep) = gridBiasesTs;
end

end