% Get pairwise distances between two coordinate sets
function D = getdistances(x1,y1,x2,y2,coordinate_system)

if strcmp(coordinate_system,'projected')

    % Use Euclidean distance for projected coordinates
    D = sqrt((x1(:)-x2(:)').^2+(y1(:)-y2(:)').^2);
elseif strcmp(coordinate_system,'geographic')

    % Use great-circle distance for longitude/latitude coordinates
    earth_radius_km = 6371;
    lon1 = deg2rad(x1(:));
    lat1 = deg2rad(y1(:));
    lon2 = deg2rad(x2(:)');
    lat2 = deg2rad(y2(:)');
    dlon = lon2-lon1;
    dlat = lat2-lat1;
    a = sin(dlat/2).^2+cos(lat1).*cos(lat2).*sin(dlon/2).^2;
    D = 2*earth_radius_km*asin(sqrt(a));
end

% Avoid division by zero in inverse-distance weighting
D(D == 0) = eps;

end