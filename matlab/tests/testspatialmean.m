function tests = testspatialmean
tests = functiontests(localfunctions);
end

function testGeographicWeights(testCase)
grid_y = [0 0;60 60];
grid = [0 0;10 10];
verifyEqual(testCase,spatialmean(grid,grid_y,'geographic'),10/3,...
    'AbsTol',1e-12);
verifyEqual(testCase,spatialmean(grid,grid_y,'projected'),5,...
    'AbsTol',1e-12);
end

function testMissingCells(testCase)
grid_y = [0 0;60 60];
grid = cat(3,[0 0;10 10],[NaN NaN;10 10]);
verifyEqual(testCase,spatialmean(grid,grid_y,'geographic'),[10/3;10],...
    'AbsTol',1e-12);
end
