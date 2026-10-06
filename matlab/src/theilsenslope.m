function slopes = theilsenslope(x,y,dim,chunk_size)
%THEILSENSLOPE Median pairwise slope along a selected array dimension.

if nargin < 3 || isempty(dim)
    dim = find(size(y) ~= 1,1,'first');
    if isempty(dim)
        dim = 1;
    end
end
if nargin < 4
    chunk_size = 5000;
end
if ~isscalar(dim) || dim < 1 || dim > ndims(y) || dim ~= fix(dim)
    error('dim must identify a dimension of y.')
end
if ~isscalar(chunk_size) || chunk_size <= 0
    error('chunk_size must be positive.')
end

x = double(x(:));
if size(y,dim) ~= numel(x)
    error('The selected y dimension must have the same length as x.')
end

order = [setdiff(1:ndims(y),dim,'stable') dim];
moved = permute(double(y),order);
output_size = size(moved);
output_size = output_size(1:end-1);
flat = reshape(moved,[],numel(x));
finite_x = isfinite(x);
x = x(finite_x);
flat = flat(:,finite_x);
slopes = nan(size(flat,1),1);

if numel(x) >= 2
    [first,second] = find(triu(true(numel(x),numel(x)),1));
    dx = x(second) - x(first);
    distinct = dx ~= 0;
    first = first(distinct);
    second = second(distinct);
    dx = dx(distinct)';

    for first_series = 1:chunk_size:size(flat,1)
        last_series = min(first_series + chunk_size - 1,size(flat,1));
        block = flat(first_series:last_series,:);
        eligible = sum(isfinite(block),2) >= 2;
        if isempty(dx) || ~any(eligible)
            continue
        end
        values = block(eligible,:);
        pairwise = (values(:,second) - values(:,first)) ./ dx;
        block_slopes = slopes(first_series:last_series);
        block_slopes(eligible) = median(pairwise,2,'omitnan');
        slopes(first_series:last_series) = block_slopes;
    end
end

if numel(output_size) < 2
    output_size = [output_size 1];
end
slopes = reshape(slopes,output_size);

end
