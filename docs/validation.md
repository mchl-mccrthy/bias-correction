# Validation

This document summarises the validation of the Python implementation against 
the original MATLAB implementation of EQM-STeP.

## Purpose

The Python implementation was validated against the MATLAB reference
implementation to confirm that both produce numerically equivalent
bias-corrected outputs when run with identical input data and configuration
settings.

The MATLAB implementation is treated as the reference workflow. The
Python implementation is treated as the main implementation, which will
be maintained.

## Test setup

Validation was performed using the Andermatt-Zuerich test domain for two
climate variables:

- `tas`: daily mean temperature, using additive bias correction
- `pr`: daily precipitation, using multiplicative bias correction

Both tests used:

- identical raw gridded NetCDF input data
- identical station observation files
- identical station coordinate files
- identical configuration settings
- monthly empirical quantile mapping
- elevation-aware inverse-distance weighting
- trend preservation enabled

The Python implementation uses Hazen empirical quantiles:

```python
np.nanquantile(values, probabilities, method="hazen")
```

to match MATLAB's `quantile` behaviour.

## Comparison method

For each variable, the Python and MATLAB bias-corrected NetCDF outputs were
loaded and compared grid cell by grid cell and timestep by timestep.

The difference was calculated as:

```text
Python output - MATLAB output
```

The following summary statistics were calculated from absolute differences:

- maximum absolute difference
- mean absolute difference
- median absolute difference
- 90th, 95th, 99th, and 99.9th percentile absolute differences

## Results

### Temperature (`tas`)

For `tas`, with additive bias correction and trend preservation enabled:

| Statistic | Absolute difference |
|---|---:|
| Maximum | 0.009621 degC |
| Mean | 0.000000 degC |
| Median | 0.000000 degC |
| 90th percentile | 0.000001 degC |
| 95th percentile | 0.000001 degC |
| 99th percentile | 0.000002 degC |
| 99.9th percentile | 0.000002 degC |

The maximum difference occurred at one grid cell and timestep. Further
inspection showed that this was caused by a near-tie in nearest-quantile
selection after detrending. Two adjacent detrended raw quantiles were almost
equally close to the target value, leading MATLAB and Python to select adjacent
quantile corrections. The resulting difference was approximately 0.0096 degC.
This is a numerical tie-breaking effect rather than a methodological
difference.

### Precipitation (`pr`)

For `pr`, with multiplicative bias correction and trend preservation enabled:

| Statistic | Absolute difference |
|---|---:|
| Maximum | 0.000470 |
| Mean | 0.000000 |
| Median | 0.000000 |
| 90th percentile | 0.000000 |
| 95th percentile | 0.000001 |
| 99th percentile | 0.000002 |
| 99.9th percentile | 0.000005 |

The precipitation differences were negligible and consistent with numerical
precision effects.

## Conclusion

The Python and MATLAB implementations produce numerically equivalent results
for both additive and multiplicative workflows. Remaining
differences are negligible for practical use and arise from floating-point
precision and near-tie quantile selection.

The Python implementation is therefore considered validated against the MATLAB
reference implementation for the tested configurations.

## Version information

Validation should be tied to the exact archived code version used for the
paper. Update this section after committing and tagging the publication
release.

- Validation date: 2026-07-16
- Current repository commit at time of drafting: `d4703eb`
- Publication release: to be updated
