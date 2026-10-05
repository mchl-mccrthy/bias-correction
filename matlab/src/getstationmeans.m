function [station_means,raw_means,bc_means] = getstationmeans(station,raw,bc)
% Means of yearly values over coincident valid years.
station_values = station{:,:};
raw_values = raw{:,:};
bc_values = bc{:,:};
valid = ~isnan(station_values) & ~isnan(raw_values) & ~isnan(bc_values);
station_values(~valid) = NaN;
raw_values(~valid) = NaN;
bc_values(~valid) = NaN;
station_means = mean(station_values,1,'omitnan');
raw_means = mean(raw_values,1,'omitnan');
bc_means = mean(bc_values,1,'omitnan');
end
