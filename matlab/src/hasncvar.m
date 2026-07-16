% Check whether a NetCDF file contains a variable
function tf = hasncvar(file_path,var_name)

info = ncinfo(file_path);
var_names = {info.Variables.Name};
tf = any(strcmp(var_names,var_name));

end