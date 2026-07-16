# EQM-STeP v0.1.0

A workflow for bias correction of historical gridded climate data using station observations and empirical quantile mapping, with the option to preserve station trends. 

There are two implementations: one MATLAB and one Python. The Python implementation is the main one, which was ported from the MATLAB implementation, which is the original/reference. The Python port was validated against the MATLAB implementation.

**Author:** Michael McCarthy

## Features

- Empirical quantile mapping
- Monthly, seasonal, or whole-period corrections
- Additive or multiplicative bias correction
- Optional preservation of station trends
- Spatial interpolation of station-based corrections using inverse-distance weighting (IDW)
- Optional parallel processing
- NetCDF input and output
- Diagnostic maps, trend comparisons, and quantile-quantile plots

## How to use this software

The workflow has three stages:
1. Bias-correct raw gridded climate data using station observations.
2. Calculate diagnostics from the station, raw gridded and bias-corrected gridded climate data.
3. Make diagnostic plots.

Example runners are provided in `matlab/run_bias_correction.m` and
`scripts/run_bias_correction.py`.

These contain calls to three functions:
1. **`runbiascorrection`**
   - Applies the bias correction
   - Optionally writes the bias-corrected dataset to a NetCDF file
2. **`makediagnostics`**
   - Reloads the raw, station, and bias-corrected datasets
   - Computes diagnostic statistics and stores them in a diagnostics structure
3. **`makeplots`**
   - Produces diagnostic figures including:
     - Maps
     - Time series at stations
     - Trend comparisons
     - Quantile-quantile plots

### Python
In Python, run the following from the repository root:
```powershell
python -m scripts.run_bias_correction
```
This script loads a configuration file from /scripts, does the bias correction, computes 
diagnostics and plots figures.

### MATLAB
In MATLAB, run the following from the repository root:
```matlab
matlab/run_bias_correction.m
```
This script loads a configuration file from /matlab/config, does the bias correction, computes 
diagnostics and plots figures.

> **Note**
>
> `makediagnostics` expects the bias-corrected NetCDF file to exist at `cfg.file_path_bc_data`.
>
> - For a complete end-to-end run, set
>
>   ```matlab
>   cfg.write_output = true;
>   ```
>
> - If
>
>   ```matlab
>   cfg.write_output = false;
>   ```
>
>   the bias-corrected NetCDF file must already exist.

## Configuration

Workflow settings are defined in the example configuration files under
`matlab/config/` and `scripts/`.

| Setting | Description |
|---------|-------------|
| `clim_var_name` | Climate variable name in both the NetCDF and station files |
| `qmf_period` | Quantile mapping period (`whole`, `seasonal`, or `monthly`) |
| `bc_type` | Bias-correction type (`additive` or `multiplicative`) |
| `preserve_trends` | Preserve observed station trends |
| `trend_window` | Moving-average window length used for trend estimation |
| `agg_method` | Annual aggregation method (`mean` or `sum`) |
| `write_output` | Write the corrected NetCDF file |
| `n_quantiles` | Number of empirical quantiles |
| `idw_power` | Inverse-distance weighting exponent |
| `multiplicative_epsilon` | Offset used for multiplicative detrending/retrending |
| `use_parallel` | Enable parallel processing |
| `n_workers` | Number of parallel workers (`[]` uses the MATLAB default) |
| `keep_grid_biases` | Keep interpolated quantile-mapping bias grids in results |
| `coordinate_system` | Coordinate type for IDW distances (`geographic` or `projected`) |
| `idw_method` | Use normal or elevation-aware IDW distances (`horizontal` or `elevation_aware`) |
| `idw_alpha` | Scaling parameter for elevation-aware IDW |

## Data requirements

The workflow assumes:

- Raw gridded climate data are supplied as NetCDF files containing:
  - `x, lon, longitude`
  - `y, lat, latitude`
  - `time`
- Station observations cover the same period as the gridded dataset.
- Missing station observations are represented by `NaN`.
- The climate variable name is consistent between the NetCDF and station datasets.

## Notes

- When station trend corrections are unavailable, the trend correction is set to a neutral value so the raw gridded trend is retained.
- For geographic coordinates, IDW distances are calculated using great-circle distance. For projected coordinates, they are calculated using Euclidean distance.
- For IDW with elevation-aware distances, projected coordinates and elevation are assumed to be in metres.

## Repository structure

```text
bias_correction/
|-- docs/
|-- eqm_step/
|-- matlab/
|-- scripts/
|-- README.md
|-- pyproject.toml
|-- LICENSE
`-- .gitignore
```
