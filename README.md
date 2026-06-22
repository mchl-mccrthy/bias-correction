# bias-correction

A MATLAB workflow for bias correction of historical gridded climate datasets using station observations and empirical quantile mapping, with option to preserve station trends.

Author: Michael McCarthy

## Features
- Empirical quantile mapping
- Monthly, seasonal, or whole-period corrections
- Spatial interpolation of station-based corrections
- Optional trend preservation
- NetCDF input/output

## Workflow
1. Load station and raw gridded climate data
2. Get trends
3. Detrend
4. Derive station-specific quantile mapping functions
5. Spatially interpolate bias corrections
6. Apply bias corrections to the gridded dataset
7. Retrend
8. Export bias corrected gridded climate data

## Repository Structure
```
bias_correction/
├── src/
├── input_data/
├── output_data/
├── README.md
└── .gitignore
```
