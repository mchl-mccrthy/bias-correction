% Unit tests for EQTM plot unit labels
function tests = testunits

tests = functiontests(localfunctions);

end

% Add MATLAB source folder to the path
function setupOnce(~)

test_dir = fileparts(mfilename('fullpath'));
addpath(fullfile(test_dir,'..','src'))

end

% Mean aggregation keeps native units and trends add per-year units
function testMeanUnits(testCase)

verifyEqual(testCase,yearlyunits('K','mean'),'K')
verifyEqual(testCase,trendunits('K','mean'),'K year^{-1}')

end

% Sum aggregation adds yearly denominators
function testSumUnits(testCase)

verifyEqual(testCase,yearlyunits('mm','sum'),'mm year^{-1}')
verifyEqual(testCase,trendunits('mm','sum'),'mm year^{-2}')

end

% Compact daily denominators are removed before yearly units are added
function testCompactDailyDenominator(testCase)

verifyEqual(testCase,yearlyunits('kg m-2 day-1','sum'),...
    'kg m^{-2} year^{-1}')
verifyEqual(testCase,trendunits('kg m-2 day-1','sum'),...
    'kg m^{-2} year^{-2}')

end

% Braced daily denominators are removed before yearly units are added
function testBracedDailyDenominator(testCase)

verifyEqual(testCase,yearlyunits('kg m^{-2} day^{-1}','sum'),...
    'kg m^{-2} year^{-1}')
verifyEqual(testCase,trendunits('kg m^{-2} day^{-1}','sum'),...
    'kg m^{-2} year^{-2}')

end

% Zero alpha gives horizontal distances without requiring elevation
function testZeroAlphaDistance(testCase)

D = getdistances(3,4,0,0,'projected',[],[],0);
verifyEqual(testCase,D,5,'AbsTol',1e-12)

end

% Positive alpha combines horizontal and elevation distances
function testPositiveAlphaDistance(testCase)

D = getdistances(3,4,0,0,'projected',1,0,10);
verifyEqual(testCase,D,sqrt(125),'AbsTol',1e-12)

end

% Positive alpha requires elevation data
function testPositiveAlphaRequiresElevation(testCase)

did_error = false;
try
    getdistances(3,4,0,0,'projected',[],[],10);
catch
    did_error = true;
end
verifyTrue(testCase,did_error)

end

% Quantile corrections are interpolated between adjacent raw quantiles
function testQuantileBiasInterpolation(testCase)

verifyEqual(testCase,interpolatequantilebias(5,[0;10;20],[1;3;9]),2)
verifyEqual(testCase,interpolatequantilebias(10,[0;10;20],[1;3;9]),3)

end

% Quantile interpolation clamps tails and retains the first duplicate
function testQuantileBiasInterpolationEndpointsAndDuplicates(testCase)

verifyEqual(testCase,interpolatequantilebias(-1,[0;10],[2;4]),2)
verifyEqual(testCase,interpolatequantilebias(11,[0;10],[2;4]),4)
verifyEqual(testCase,interpolatequantilebias(0,[0;0;10],[1;4;5]),1)
verifyEqual(testCase,interpolatequantilebias(5,[0;0;10],[1;4;5]),3)

end

% Station coordinates are matched to climate-data station columns
function testStationCoordinatesMatchedToClimateColumns(testCase)

tmp_dir = tempname;
mkdir(tmp_dir)
cleanup = onCleanup(@() rmdir(tmp_dir,'s'));

station_clim = table(2000,1,1,1,2,...
    'VariableNames',{'year','month','day','A','B'});
station_coords = table(["Unused";"B";"A"],[0;20;10],[0;200;100],[0;2;1],...
    'VariableNames',{'station','lat','lon','z'});

file_path_station_clim_var = fullfile(tmp_dir,'station_clim.csv');
file_path_station_coords = fullfile(tmp_dir,'station_coords.csv');
writetable(station_clim,file_path_station_clim_var)
writetable(station_coords,file_path_station_coords)

[station_clim_var,station_coords_out,station_x,station_y,station_z,~] = ...
    loadstationdata(file_path_station_clim_var,file_path_station_coords);

verifyEqual(testCase,station_clim_var.Properties.VariableNames,{'A','B'})
verifyEqual(testCase,string(station_coords_out.station)',["A" "B"])
verifyEqual(testCase,station_x',[100 200])
verifyEqual(testCase,station_y',[10 20])
verifyEqual(testCase,station_z',[1 2])

end

% Missing station coordinates throw a clear error
function testMissingStationCoordinatesError(testCase)

tmp_dir = tempname;
mkdir(tmp_dir)
cleanup = onCleanup(@() rmdir(tmp_dir,'s'));

station_clim = table(2000,1,1,1,2,...
    'VariableNames',{'year','month','day','A','B'});
station_coords = table("A",10,100,...
    'VariableNames',{'station','lat','lon'});

file_path_station_clim_var = fullfile(tmp_dir,'station_clim.csv');
file_path_station_coords = fullfile(tmp_dir,'station_coords.csv');
writetable(station_clim,file_path_station_clim_var)
writetable(station_coords,file_path_station_coords)

verifyError(testCase,@() loadstationdata(file_path_station_clim_var,...
    file_path_station_coords),'EQTM:loadstationdata:StationMissing')

end
