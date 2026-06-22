function [X,Y,Z] = prepsd(X,Y,Z)

X = X(:);
Y = Y(:);
Z = Z(:);

cond = isfinite(X) & isfinite(Y) & isfinite(Z);

X = X(cond);
Y = Y(cond);
Z = Z(cond);

end