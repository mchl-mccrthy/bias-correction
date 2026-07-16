% Detrend climate data
function clim_data_detrended = detrendclimdata(clim_data,trends,bc_type,...
    multiplicative_epsilon)

% Remove trends
if strcmp(bc_type,'additive')
    clim_data_detrended = clim_data-trends;
else
    clim_data_detrended = (clim_data+multiplicative_epsilon)./...
        (trends+multiplicative_epsilon);
end

end