# EQTM v0.2.0

A software for bias correcting historical gridded climate data using station observations via empirical quantile mapping, with optional trend mapping.

**Author:** Michael McCarthy

## Features

- Empirical quantile mapping
- Optional trend mapping
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
It loads an Andermatt-Zurich example configuration file from `scripts/`, runs
the bias correction, computes diagnostics and plots figures.

The Switzerland-wide paper experiments use separate configurations in
`paper/scripts/`. They require substantially more memory than the lightweight
example and are intended to be run on a compute node:

```powershell
python -m paper.scripts.run_paper_all
```

To regenerate figures and the in-sample table from existing outputs only:
```powershell
python -m paper.scripts.make_outputs
```
Individual scripts include `make_maps`, `make_elevation_plots`, `make_qq_plots`,
`make_quantile_residual_plots`, `make_annual_mae_plots`,
`make_quantile_mae_plots`, `make_trend_ae_plots`, `make_trend_scatter_plots`,
and `make_diagnostics_table`. Use `python -m paper.scripts.<name>` to run one.
`cross_validation` runs the five-fold experiments, while `compare_matlab_python`
runs the implementation comparison. The per-variable runners are `run_eqtm_tas`
and `run_eqtm_pr`.

The in-sample and cross-validation summary CSVs retain three method rows and
six metric columns, with units in the metric headings. The detailed
cross-validation CSV uses separate quantile, yearly and trend unit columns
because temperature and precipitation share the same metric columns. The
MATLAB-Python comparison likewise reports native units in its `Units` column.
CSV units are plain text (for example, `mm year^-2`), not plotting markup.

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
| `trend_mapping` | Enable or disable trend mapping (`true` or `false`) |
| `trend_window` | Moving-average window length used for trend estimation |
| `agg_method` | Annual aggregation method (`mean` or `sum`) |
| `write_output` | Write the corrected NetCDF file |
| `n_quantiles` | Number of empirical quantiles |
| `idw_power` | Inverse-distance weighting exponent |
| `idw_alpha` | Elevation scaling for IDW distances; `0` uses horizontal distances only |
| `multiplicative_epsilon` | Offset used for multiplicative detrending/retrending |
| `use_parallel` | Enable parallel processing over time steps |
| `n_workers` | Number of parallel workers (`None` in Python or `[]` in MATLAB uses the environment default) |
| `keep_grid_biases` | Keep interpolated quantile-mapping bias grids in results |
| `coordinate_system` | Coordinate type for IDW distances (`geographic` or `projected`) |

Both implementations parallelise quantile mapping over independent time steps
using separate worker processes. On Windows, run a parallel workflow from a
script protected by `if __name__ == "__main__":`, as in the supplied runners.

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
- Time-specific station corrections are linearly interpolated between
  corrections at adjacent empirical raw-grid quantiles. Values outside the
  fitted range use the nearest endpoint correction; repeated raw quantiles
  retain the correction at their first occurrence.
- For multiplicative correction, a zero raw quantile is assigned the neutral
  factor 1. This preserves zero values without allowing an undefined ratio to
  distort the spatial interpolation; EQTM does not adjust wet-day occurrence.
- `makediagnostics` writes `<variable>_diagnostics_summary.csv` in `overview/`
  and `<station>_<variable>_diagnostics_summary.csv` in `individual_stations/`,
  both under `file_path_figures_tables`. Each table has Raw and Bias-corrected
  rows, with quantile/yearly errors, means, and Theil-Sen slopes. Station tables
  include observed and model means of yearly values over coincident valid years.
  Overview tables instead include the domain yearly mean and the linear
  trend fitted to the yearly spatial-average series. Geographic grids use
  cell-area weights proportional to the cosine of latitude; projected grids
  use equal cell weights.
  Error metrics in the overview remain equal-weight averages across stations;
  trend errors are AE per station and MAE in the overview.
  CSV headings include plain-text units in both implementations. For precipitation
  configured in mm/day with sum aggregation, mean yearly values and yearly MAE
  use mm year^-1, trends and trend errors use mm year^-2, and quantile MAE uses
  mm day^-1. Internal summary-table metric names are unchanged for paper scripts.

## Repository structure

```text
bias_correction/
|-- docs/
|-- eqtm/
|-- input_data/        # Included in Zenodo archive, ignored by GitHub
|   `-- andermatt_zurich_1981_2020/
|       |-- gridded/
|       `-- station/
|-- matlab/
|-- output_data/       # Generated outputs, ignored by GitHub
|   `-- andermatt_zurich_1981_2020/
|       |-- figures_and_tables/
|       |   |-- individual_stations/  # Per-station figures and CSV tables
|       |   `-- overview/             # Study-wide figures and CSV tables
|       `-- gridded/                  # Bias-corrected NetCDF files
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
