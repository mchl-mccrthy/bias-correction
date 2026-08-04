% Append an additional unit factor with clean spacing
function out_units = appendunitfactor(base_units,factor)

% Avoid leading whitespace if no base units are present
if isempty(base_units)
    out_units = factor;
else
    out_units = [base_units ' ' factor];
end

end
