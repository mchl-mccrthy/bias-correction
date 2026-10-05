% Save bias-corrected climate data
function savebcdata(bc_clim_var,file_path_raw_data,file_path_bc_data,...
    clim_var_name,cfg)

% Create output folder if needed
output_folder = fileparts(file_path_bc_data);
if ~exist(output_folder,'dir')
    mkdir(output_folder)
end

% Permute data back to ECMWF standard
bc_clim_var = permute(bc_clim_var,[2 1 3]);

% Copy the raw NetCDF structure and replace the climate variable with 
% bias-corrected data
copyfile(file_path_raw_data,file_path_bc_data);
ncwrite(file_path_bc_data,clim_var_name,bc_clim_var);

% Update documentation
ncwriteatt(file_path_bc_data,clim_var_name,'bias_correction',...
   'EQTM: empirical quantile and trend mapping');
ncwriteatt(file_path_bc_data,clim_var_name,'eqtm_version',...
   eqtmversion());
ncwriteatt(file_path_bc_data,clim_var_name,'eqtm_reference',...
   'https://github.com/mchl-mccrthy/bias-correction');
ncwriteatt(file_path_bc_data,clim_var_name,'eqtm_parameters',...
   eqtmparameters(cfg));
ncwriteatt(file_path_bc_data,'/','history',...
   sprintf('%s: replaced %s with bias-corrected data (EQTM)',...
   datestr(now,30),clim_var_name));

end

% Get EQTM version used for output metadata
function out = eqtmversion()

out = '0.2.0';

end

% Format key EQTM parameters for output metadata
function out = eqtmparameters(cfg)

parts = { ...
    ['bc_type=' char(cfg.bc_type)], ...
    ['qmf_period=' char(cfg.qmf_period)], ...
    ['trend_mapping=' logicaltext(cfg.trend_mapping)], ...
    ['trend_window=' num2str(cfg.trend_window)], ...
    ['agg_method=' char(cfg.agg_method)], ...
    ['n_quantiles=' num2str(cfg.n_quantiles)], ...
    ['idw_power=' num2str(cfg.idw_power)], ...
    ['idw_alpha=' num2str(cfg.idw_alpha)], ...
    ['coordinate_system=' char(cfg.coordinate_system)], ...
    ['multiplicative_epsilon=' num2str(cfg.multiplicative_epsilon)]};
out = strjoin(parts,'; ');

end

% Convert logical scalar to text for metadata
function out = logicaltext(value)

if value
    out = 'true';
else
    out = 'false';
end

end
