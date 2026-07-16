% Get row and column of sample point in a 2d array that is closest to a 
% query point

function [row,col] = indexofclosest2(xq,yq,x,y)

% Get x, y and query x, y into correct format
xyQ = [xq,yq];
xy = [x(:),y(:)];

% Search for closest points
k = dsearchn(xy,xyQ);

% Get rows and columns
[nRows,nCols] = size(x);
[row,col] = ind2sub([nRows,nCols],k);

end