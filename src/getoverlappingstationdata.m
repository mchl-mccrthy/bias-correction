% Get overlapping valid data for one station
function [station_overlap,raw_overlap,bc_overlap] = ...
    getoverlappingstationdata(station_clim_var,raw_station_clim_var,...
    bc_station_clim_var,station_time,raw_time,i_station)

% Get data
raw_tmp = raw_station_clim_var{:,i_station};
bc_tmp = bc_station_clim_var{:,i_station};
station_tmp = station_clim_var{:,i_station};

% Get intersection indices
[~,ia,ib] = intersect(raw_time,station_time);

% Get overlapping data
raw_overlap = raw_tmp(ia);
bc_overlap = bc_tmp(ia);
station_overlap = station_tmp(ib);

% Which data are valid?
valid = ~isnan(raw_overlap) & ...
        ~isnan(bc_overlap) & ...
        ~isnan(station_overlap);

% Remove invalid data 
raw_overlap = raw_overlap(valid);
bc_overlap = bc_overlap(valid);
station_overlap = station_overlap(valid);

end