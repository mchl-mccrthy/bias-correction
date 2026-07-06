# bias-correction

A MATLAB workflow for bias correction of historical gridded climate datasets using station observations and empirical quantile mapping, with option to preserve station trends.

Author: Michael McCarthy

## Features
- Empirical quantile mapping
- Monthly, seasonal, or whole-period corrections
- Additive or multiplicative correction
- Optional preservation of station trends
- Spatial interpolation of station-based corrections by inverse-distance weighting
- Optional parallel processing
- NetCDF input/output
- Diagnostic plots for bias-corrected data

## Workflow
The top-level script bias_correction.m runs three stages:

results = runbiascorrection(cfg);
diagnostics = makediagnostics(cfg);
makeplots(diagnostics,cfg);

runbiascorrection applies the bias correction and optionally writes a bias-corrected NetCDF file.
makediagnostics reloads the raw, station, and bias-corrected data and prepares diagnostic summaries in memory.
makeplots creates maps, station diagnostics, trend comparisons, and quantile-quantile plots from the diagnostics struct.

makediagnostics expects the bias-corrected NetCDF file at cfg.file_path_bc_data. For a fresh end-to-end run, set cfg.write_output = true. If cfg.write_output = false, the bias-corrected file must already exist.

## Configuration
Workflow settings are defined in files under config/. The main settings are:
- clim_var_name: variable name in the NetCDF and station files.
- qmf_period: quantile mapping period, one of whole, seasonal, or monthly.
- bc_type: correction type, either additive or multiplicative.
- preserve_trends: whether to preserve station trends.
- trend_window: moving-mean window length in time steps.
- agg_method: yearly aggregation method, either mean or sum.
- write_output: whether to write the bias-corrected NetCDF file.
- n_quantiles: number of quantiles used for empirical quantile mapping.
- idw_power: inverse-distance weighting exponent.
- multiplicative_epsilon: offset used for multiplicative detrending/retrending.
- use_parallel: whether to use parallel processing.
- n_workers: number of parallel workers, or [] for the MATLAB default.

## Data Requirements
Raw gridded climate data should be provided as NetCDF with lon, lat, and time variables.
Station data should cover the same period as the gridded data.
Missing station values should be represented as NaN.
The climate variable name should match between the station data and the NetCDF file.

## Repository Structure
bias_correction/
|-- bias_correction.m
|-- config/
|-- src/
|-- archive/
|-- input_data/
|-- output_data/
|-- README.md
`-- .gitignore