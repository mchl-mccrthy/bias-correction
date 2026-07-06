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
The top-level script `bias_correction.m` runs three stages:

```matlab
results = runbiascorrection(cfg);
diagnostics = makediagnostics(cfg);
makeplots(diagnostics,cfg);

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
