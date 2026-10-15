# Validation

This document summarises the validation of the Python implementation against 
the original MATLAB implementation of EQTM.

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
- inverse-distance weighting with elevation scaling
- trend mapping enabled

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

### Repeating the comparison for Switzerland

`python -m paper.scripts.run_paper_all` checks that MATLAB can start, runs
the four Python paper configurations, and then runs their MATLAB counterparts
before cross-validation and paper plotting. MATLAB must be on `PATH`; the
MATLAB Parallel Computing Toolbox is needed when parallel processing is enabled.
Slurm is not required by the scripts.

To compare existing Python paper outputs independently, run:

```bash
python -m paper.scripts.compare_matlab_python
```

The MATLAB configurations are generated from the Python configurations. The
comparison loads one full output pair at a time and checks coordinates, times,
shapes, and missing-value masks. Shared missing cells are excluded. The CSV
reports mean and maximum absolute differences and the x/y coordinates and time
of the first maximum for tas and pr, with trend mapping on and off.

The table is saved in `paper/figures_and_tables/matlab_python_comparison.csv`
and in `matlab_python_comparison/` alongside the experiment's `trends_on/`
and `trends_off/` output folders. Each run retains its JSON configuration and
MATLAB log there. Its temporary MATLAB NetCDF is deleted only after comparison
results have been saved; failed runs retain their files for inspection.
Standalone comparisons assume the Python outputs match the current configs
and code.

### Temperature (`tas`)

For the Andermatt-Zurich example, using linearly interpolated quantile
corrections:

| Trend mapping | Mean absolute difference | Maximum absolute difference |
|---|---:|---:|
| On | 0.000013 degC | 0.005649 degC |
| Off | 0.000011 degC | 0.000111 degC |

Interpolation avoids discontinuous changes between adjacent quantile
corrections when MATLAB and Python represent packed NetCDF values at slightly
different floating-point precision.

### Precipitation (`pr`)

For the same example:

| Trend mapping | Mean absolute difference | Maximum absolute difference |
|---|---:|---:|
| On | 0.000000163 mm day^-1 | 0.000290 mm day^-1 |
| Off | 0.000000111 mm day^-1 | 0.000046 mm day^-1 |

The precipitation differences were negligible and consistent with numerical
precision effects.

## Conclusion

The Python and MATLAB implementations produce numerically equivalent results
for both additive and multiplicative workflows. Remaining
differences are negligible for practical use and arise from floating-point
precision in numerical operations.

The Python implementation is therefore considered validated against the MATLAB
reference implementation for the tested configurations.

## Version information

Validation should be tied to the exact archived code version used for the
paper. Update this section after committing and tagging the publication
release.

- Validation date: 2026-10-15
- Current repository commit at time of drafting: to be updated after commit
- Publication release: to be updated
