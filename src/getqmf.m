% Get quantile mapping function
function qmf = getqmf(stnDatetime,stnVar,reaDatetime,reaVar)

% Make tables
stnData = table(stnDatetime,stnVar);
reaData = table(reaDatetime,reaVar);

% Retime AWS data to reanalysis data
reaData = table2timetable(reaData);
stnData = table2timetable(stnData);
stnData = retime(stnData,reaData.reaDatetime);

% Get variable data from tables
varAws = stnData.stnVar;
varRea = reaData.reaVar;

% Remove NaNs from both datasets (although there should be none in the 
% reanalysis)
makeNan = isnan(varRea) | isnan(varAws);
varRea(makeNan) = NaN;
varAws(makeNan) = NaN;

% Specify number of quantiles
nQs = 1001;
qs = linspace(0,1,nQs);

% Get quantiles
varAwsQ = quantile(varAws,qs);
varReaQ = quantile(varRea,qs);

% Get mapping function
qmf = complex(varAwsQ,varReaQ);

end
