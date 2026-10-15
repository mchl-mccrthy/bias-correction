% Interpolate a correction between adjacent empirical raw quantiles.
function bias = interpolatequantilebias(raw_value,raw_quantiles,...
    quantile_biases)

if ~isfinite(raw_value)
    bias = NaN;
    return
end

raw_quantiles = raw_quantiles(:);
quantile_biases = quantile_biases(:);
valid = isfinite(raw_quantiles) & isfinite(quantile_biases);
if ~any(valid)
    bias = NaN;
    return
end

x = raw_quantiles(valid);
corrections = quantile_biases(valid);

% Empirical quantiles can repeat, particularly for zero precipitation.
% Retain the first correction to preserve the lower-quantile convention.
keep = [true; diff(x) ~= 0];
x = x(keep);
corrections = corrections(keep);

if numel(x) == 1 || raw_value <= x(1)
    bias = corrections(1);
    return
elseif raw_value >= x(end)
    bias = corrections(end);
    return
end

i_upper = find(x >= raw_value,1,'first');
if x(i_upper) == raw_value
    bias = corrections(i_upper);
    return
end

i_lower = i_upper-1;
fraction = (raw_value-x(i_lower))/(x(i_upper)-x(i_lower));
bias = corrections(i_lower)+...
    fraction*(corrections(i_upper)-corrections(i_lower));

end
