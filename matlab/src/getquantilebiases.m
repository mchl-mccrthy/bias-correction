% Calculate additive or multiplicative station quantile corrections.
function biases = getquantilebiases(station_quantiles,raw_quantiles,bc_type)

if strcmp(bc_type,'multiplicative')
    biases = station_quantiles./raw_quantiles;

    % A zero model quantile cannot be adjusted multiplicatively. A factor
    % of one is neutral and avoids distorting the spatial interpolation.
    zero_denominator = raw_quantiles == 0 & isfinite(station_quantiles);
    biases(zero_denominator) = 1;
elseif strcmp(bc_type,'additive')
    biases = station_quantiles-raw_quantiles;
else
    error('EQTM:getquantilebiases:InvalidBcType',...
        'bc_type must be ''additive'' or ''multiplicative''.')
end

end
