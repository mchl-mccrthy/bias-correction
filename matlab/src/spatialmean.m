% Spatial mean with grid-cell area weighting for geographic coordinates
function out = spatialmean(grid,grid_y,coordinate_system)

if ~isequal(size(grid,[1 2]),size(grid_y))
    error('grid_y must match the first two dimensions of grid.')
end

if strcmp(coordinate_system,'geographic')
    weights = cosd(grid_y);
elseif strcmp(coordinate_system,'projected')
    weights = ones(size(grid_y));
else
    error('coordinate_system must be ''projected'' or ''geographic''.')
end

n_cells = numel(weights);
grid_2d = reshape(grid,n_cells,[]);
weights = weights(:);
out_values = NaN(size(grid_2d,2),1);
chunk_size = 64;
for first = 1:chunk_size:size(grid_2d,2)
    last = min(first+chunk_size-1,size(grid_2d,2));
    values = double(grid_2d(:,first:last));
    valid = isfinite(values);
    values(~valid) = 0;
    numerator = sum(values.*weights,1);
    denominator = sum(valid.*weights,1);
    chunk = numerator./denominator;
    chunk(denominator == 0) = NaN;
    out_values(first:last) = chunk;
end

if ismatrix(grid)
    out = out_values(1);
else
    grid_size = size(grid);
    out = squeeze(reshape(out_values,[1 1 grid_size(3:end)]));
end

end
