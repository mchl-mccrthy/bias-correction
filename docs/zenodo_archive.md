# Zenodo archive plan

The GitHub repository is kept small and source-code focused. Large NetCDF input
files and generated outputs are intentionally not tracked in Git. For the paper,
the frozen Zenodo archive should contain everything needed to reproduce the
reported workflow and figures.

## Intended archive contents

```text
EQTM-v1.0.0/
|-- eqtm/
|-- matlab/
|-- scripts/
|-- docs/
|-- input_data/
|   |-- boundaries/
|   `-- andermatt_zuerich_1981_2019/
|       |-- gridded/
|       `-- station/
|-- output_data/
|   `-- andermatt_zuerich_1981_2019/
|       |-- trends_off/
|       |   |-- figures/
|       |   `-- gridded/
|       `-- trends_on/
|           |-- figures/
|           `-- gridded/
|-- paper_figures/
|-- README.md
|-- pyproject.toml
|-- LICENSE
`-- CITATION.cff
```

## Archive requirements

- Include the exact source code version used in the paper.
- Include the Andermatt-Zurich input data used for the published examples.
- Include the Natural Earth Switzerland boundary file used for the locator map.
- Include the configuration files used to run the examples.
- Use relative paths in all archived configuration files.
- Place gridded inputs in `input_data/andermatt_zuerich_1981_2019/gridded/`
  and station inputs in `input_data/andermatt_zuerich_1981_2019/station/`.
- Write bias-corrected gridded outputs to
  `output_data/andermatt_zuerich_1981_2019/trends_on/gridded/` and
  `output_data/andermatt_zuerich_1981_2019/trends_off/gridded/`.
- Write diagnostic figures to
  `output_data/andermatt_zuerich_1981_2019/trends_on/figures/` and
  `output_data/andermatt_zuerich_1981_2019/trends_off/figures/`.
- Include scripts used to create the paper figures.
- Include either generated reference outputs or instructions for recreating
  them from the input data.
- Include validation notes comparing the Python and MATLAB implementations.
- Cite the Zenodo DOI in the paper's Code and data availability section.

## GitHub exclusions

The following are ignored in GitHub because they are large or generated:

```text
input_data/
output_data/
archive/
*.nc
*.mat
```

These files can still be included in the final Zenodo archive.

## Pre-archive checklist

1. Confirm that the Python runner works from the archive root:

   ```powershell
   python -m scripts.run_eqtm
   ```

2. Confirm that the Python paper experiments runner works from the archive root:

   ```powershell
   python -m scripts.run_paper_experiments
   ```

3. Confirm that the MATLAB runner works from the archive root:

   ```matlab
   run('matlab/run_eqtm.m')
   ```

4. Confirm that paper figure scripts run from the archive root.
5. Confirm that no configuration files contain private absolute paths.
6. Confirm that the version number in `README.md`, `pyproject.toml`, and
   `CITATION.cff` matches the Git tag and Zenodo version.
7. Confirm that the archive includes `LICENSE` and the code licence is stated
   in the paper.
