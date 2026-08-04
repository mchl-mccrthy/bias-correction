% Remove terminal inverse timestep units such as day-1 or day^{-1}
function base_units = stripterminalinversetimestep(units)

% Convert to character vector and trim whitespace
base_units = strtrim(char(units));

% Remove terminal day/hour inverse timestep variants
pattern = ['(^|\s+)(day|days|d|hour|hours|hr|hrs|h)' ...
    '(-1|\^-?1|\^\{-?1\}|\$\^\{-?1\}\$)\s*$'];
base_units = regexprep(base_units,pattern,'','ignorecase');
base_units = strtrim(base_units);

end
