function trends = get_trends(clim_data, dim, window)

sz = size(clim_data);

perm = 1:max(ndims(clim_data),dim);
perm([1 dim]) = [dim 1];

data_perm = permute(clim_data,perm);
data_2d = reshape(data_perm,sz(dim),[]);

trend_2d = movmean(data_2d,window,1,'omitnan');

trend_perm = reshape(trend_2d,size(data_perm));
trends = ipermute(trend_perm,perm);

end