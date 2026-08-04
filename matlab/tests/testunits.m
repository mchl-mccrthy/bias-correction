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

