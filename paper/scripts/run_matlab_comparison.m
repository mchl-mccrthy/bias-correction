function run_matlab_comparison(config_file)
% Run the MATLAB counterpart of a Python paper configuration.
repo_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(repo_root,'matlab','src'))
cfg = jsondecode(fileread(config_file));
disp(['MATLAB version: ' version])
disp(cfg)
biascorrect(cfg);
end
