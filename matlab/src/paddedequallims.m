% Add small padding to equal x/y limits
function lims = paddedequallims(lim_min,lim_max)

% Get span of data limits
span = lim_max - lim_min;

% Use 5% padding, with fallback for zero-width limits
if ~isfinite(span) || span <= 0
    if lim_min == 0
        pad = 0.5;
    else
        pad = abs(lim_min)*0.05;
    end
else
    pad = span*0.05;
end

% Return padded limits
lims = [lim_min - pad lim_max + pad];

end
