% Save bias-corrected climate data
function savebcdata(bc_clim_var,file_path_raw_data,file_path_bc_data,...
    clim_var_name)

% Permute data back to ECMWF standard
bc_clim_var = permute(bc_clim_var,[2 1 3]);

% Copy raw data netcdf file and write new bias corrected data netcdf file
copyfile(file_path_raw_data,file_path_bc_data);
ncwrite(file_path_bc_data,clim_var_name,bc_clim_var);

% Update documentation
ncwriteatt(file_path_bc_data,clim_var_name,'bias_correction',...
   'empirical quantile mapping');
ncwriteatt(file_path_bc_data,'/','history',...
   sprintf('%s: replaced %s with bias-corrected data (EQM)',...
   datestr(now,30),clim_var_name));

end