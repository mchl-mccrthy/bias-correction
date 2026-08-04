% Format unit exponents for plot labels
function formatted_units = formatunits(units)

% Convert to character vector and trim whitespace
formatted_units = strtrim(char(units));

% Convert common temperature spellings
formatted_units = strrep(formatted_units,'degC','\circC');

% Convert Matplotlib-style exponents to MATLAB TeX-style exponents
formatted_units = regexprep(formatted_units,'\$\^\{(-?\d+)\}\$','^{$1}');

% Convert compact inverse powers such as m-2 and day-1
formatted_units = regexprep(formatted_units,'([A-Za-z]+)-(\d+)','$1^{-$2}');

% Convert powers such as m^-2
formatted_units = regexprep(formatted_units,'([A-Za-z]+)\^(-?\d+)','$1^{$2}');

end
