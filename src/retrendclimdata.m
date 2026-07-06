% Retrend climate data
function clim_data_retrended = retrendclimdata(clim_data,trends,...
    bc_type,multiplicative_epsilon)

% Restore trends
if strcmp(bc_type,'additive')
    clim_data_retrended = clim_data+trends;
else
    clim_data_retrended = clim_data.*(trends+multiplicative_epsilon)-...
        multiplicative_epsilon;

    % Prevent negative precipitation, but preserve NaNs
    valid = ~isnan(clim_data_retrended);
    clim_data_retrended(valid) = max(clim_data_retrended(valid),0);
end

end