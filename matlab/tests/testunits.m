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
