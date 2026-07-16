% Get trends from climate data
function trends = gettrends(clim_data,dim,window)

% Get size of climate data
sz = size(clim_data);

% Permute data to get trends along time dimension
perm = 1:max(ndims(clim_data),dim);
perm([1 dim]) = [dim 1];
data_perm = permute(clim_data,perm);
data_2d = reshape(data_perm,sz(dim),[]);

% Get trends
trend_2d = movmean(data_2d,window,1,'omitnan');

% Permute trends back to shape of climate data
trend_perm = reshape(trend_2d,size(data_perm));
trends = ipermute(trend_perm,perm);

end