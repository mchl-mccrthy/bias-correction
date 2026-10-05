function tests = testquantilebiases
tests = functiontests(localfunctions);
end

function testZeroDenominatorsUseNeutralFactor(testCase)
station = [0 2 NaN 0 6];
raw = [0 0 NaN 2 3];
actual = getquantilebiases(station,raw,'multiplicative');
verifyEqual(testCase,actual,[1 1 NaN 0 2]);
end

function testAdditiveBiasesAreUnchanged(testCase)
actual = getquantilebiases([0 2 NaN],[0 1 NaN],'additive');
verifyEqual(testCase,actual,[0 1 NaN]);
end

function testUnknownBiasCorrectionTypeIsRejected(testCase)
verifyError(testCase,@() getquantilebiases(1,1,'unknown'),...
    'EQTM:getquantilebiases:InvalidBcType');
end
