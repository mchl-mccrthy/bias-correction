% Get overlapping valid data for one station
function [station_overlap,raw_overlap,bc_overlap] = ...
    getoverlappingstationdata(station_clim_var,raw_station_clim_var,...
    bc_station_clim_var,station_time,grid_time,i_station)

% Check station and grid time match
if ~isequal(station_time(:),grid_time(:))
    error('Station and grid time vectors must match exactly.')
end

% Get overlapping data
raw_overlap = raw_station_clim_var{:,i_station};
bc_overlap = bc_station_clim_var{:,i_station};
station_overlap = station_clim_var{:,i_station};

% Which data are valid?
valid = ~isnan(raw_overlap) & ...
        ~isnan(bc_overlap) & ...
        ~isnan(station_overlap);

% Remove invalid data 
raw_overlap = raw_overlap(valid);
bc_overlap = bc_overlap(valid);
station_overlap = station_overlap(valid);

end