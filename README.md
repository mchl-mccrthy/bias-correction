# bias-correction

A MATLAB workflow for bias correction of historical gridded climate datasets using station observations and empirical quantile mapping, with option to preserve station trends.

Author: Michael McCarthy

## Features
- Empirical quantile mapping
- Monthly, seasonal, or whole-period corrections
- Spatial interpolation of station-based corrections by inverse-distance weighting
- Optional preservation of trends in station data
- NetCDF input/output

## Workflow
1. Load station and raw gridded data
2. Get trends in station and raw gridded data
3. Detrend station and raw gridded data
4. Get station-specific quantile mapping functions
5. Spatially interpolate biases to grid of raw gridded data
6. Apply bias corrections to the detrended raw gridded data
7. Retrend bias corrected gridded data
8. Export bias corrected gridded data

## Repository structure
```
bias_correction/
|-- bias_correction.m
|-- config/
|-- src/
|-- archive/
|-- input_data/
|-- output_data/
|-- README.md
`-- .gitignore
```
