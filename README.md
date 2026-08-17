# EQTM v0.2.0

A software for bias correcting historical gridded climate data using station observations via empirical quantile mapping, with optional trend mapping.

**Author:** Michael McCarthy

## Features

- Empirical quantile mapping
- Optional station trend mapping
- Additive or multiplicative bias correction
- Monthly, seasonal, or whole-period bias correction
- Spatial interpolation of station-based biases and trends using inverse-distance weighting (IDW)
- Optional parallel processing
- NetCDF input and output
- Diagnostic figures and tables

## Implementation
There are two implementations of this workflow: one MATLAB and one Python. The Python implementation is the main implementation. It was ported from the original MATLAB implementation, against which it was validated. Validation results are documented in `docs/validation.md`.

## Reproducible archive

This repository is intended for source-code development and does not track
large input or output data files. The frozen version associated with a paper
will be archived on Zenodo as a single reproducible package containing the
source code, configuration files, input data, and scripts used to produce the
paper figures.

The intended archive layout is described in `docs/zenodo_archive.md`.

## How to use this workflow

The workflow has three stages:
1. Bias-correct raw gridded climate data using station observations.
2. Calculate diagnostics from the station, raw gridded and bias-corrected gridded climate data.
3. Make diagnostic plots and tables.

Example runners are provided in `matlab/run_eqtm.m` and
`scripts/run_eqtm.py`.

These runners each contain calls to three functions:
1. **`biascorrect`**
   - Applies the bias correction
   - Optionally writes the bias-corrected dataset to a NetCDF file
2. **`makediagnostics`**
   - Reloads the raw, station, and bias-corrected datasets
   - Computes diagnostic statistics and stores them in a diagnostics structure
3. **`makeplots`**
   - Produces diagnostic figures including maps, time series at stations, trend comparisons,
     quantile-quantile plots.

For a complete end-to-end run, `write_output` should be enabled in the configuration.

### Python
The Python implementation can be installed in a virtual environment using `pip`:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The example runner can then be run from the repository root:
```powershell
python -m scripts.run_eqtm
```
It loads a configuration file from `scripts/`, runs the bias correction, computes 
diagnostics and plots figures.

To reproduce the paper experiments with temperature and precipitation, with
and without station trend mapping, run:

```powershell
python -m scripts.run_paper_experiments
```

### MATLAB
In MATLAB, the example runner can be run from the repository root:
```matlab
run('matlab/run_eqtm.m')
```
It loads a configuration file from `matlab/config/`, runs the bias correction, computes 
diagnostics and plots figures.

The MATLAB implementation was developed and tested in MATLAB 2022a.

## Configuration

Workflow settings are defined in the example configuration files in
`matlab/config/` and `scripts/`.

| Setting | Description |
|---------|-------------|
| `clim_var_name` | Climate variable name in both the NetCDF and station files |
| `qmf_period` | Quantile mapping period (`whole`, `seasonal`, or `monthly`) |
| `bc_type` | Bias-correction type (`additive` or `multiplicative`) |
| `trend_method` | Trend treatment (`none` or `station`) |
| `trend_window` | Moving-average window length used for trend estimation |
| `agg_method` | Annual aggregation method (`mean` or `sum`) |
| `write_output` | Write the corrected NetCDF file |
| `n_quantiles` | Number of empirical quantiles |
| `idw_power` | Inverse-distance weighting exponent |
| `idw_alpha` | Elevation scaling for IDW distances; `0` uses horizontal distances only |
| `multiplicative_epsilon` | Offset used for multiplicative detrending/retrending |
| `use_parallel` | Enable parallel processing |
| `n_workers` | Number of parallel workers (`[]` uses the MATLAB default) |
| `keep_grid_biases` | Keep interpolated quantile-mapping bias grids in results |
| `coordinate_system` | Coordinate type for IDW distances (`geographic` or `projected`) |

## Data requirements

The workflow assumes:

- Raw gridded climate data are supplied as NetCDF files containing:
  - `x, lon, longitude`
  - `y, lat, latitude`
  - `time`
- Station observations cover the same period as the gridded dataset.
- Missing station observations are represented by `NaN`.
- Station climate-data columns define the stations used in a run. The station
  coordinate file must contain a `station` column with matching names; extra
  stations in the coordinate file are ignored.
- The climate variable name is consistent between the NetCDF and station datasets.
- For variables using `agg_method = "sum"`, terminal inverse timestep units
  such as `day^-1` are removed before yearly diagnostic units are added.
  For example, `mm day^-1` is labelled as `mm year^-1` for yearly sums and
  `mm year^-2` for trends in yearly sums.

## Notes

- When station trend corrections are unavailable, the trend correction is set to a neutral value so the raw gridded trend is retained.
- For geographic coordinates, IDW distances are calculated using great-circle distance. For projected coordinates, they are calculated using Euclidean distance.
- IDW distances include elevation when `idw_alpha > 0`. Set `idw_alpha = 0`
  for horizontal-distance IDW. For `idw_alpha > 0`, projected coordinates and
  elevation are assumed to be in metres.
- Quantile and yearly MAE diagnostics compare station values with gridded
  values extracted at station locations.

## Repository structure

```text
bias_correction/
|-- docs/
|-- eqtm/
|-- input_data/        # Included in Zenodo archive, ignored by GitHub
|   `-- andermatt_zuerich_1981_2019/
|       |-- gridded/
|       `-- station/
|-- matlab/
|-- output_data/       # Generated outputs, ignored by GitHub
|   `-- andermatt_zuerich_1981_2019/
|       |-- trends_off/
|       |   |-- figures_and_tables/
|       |   `-- gridded/
|       `-- trends_on/
|           |-- figures_and_tables/
|           `-- gridded/
|-- paper/
|   |-- figures_and_tables/
|   `-- scripts/
|-- scripts/
|-- CITATION.cff
|-- README.md
|-- pyproject.toml
|-- LICENSE
`-- .gitignore
```
