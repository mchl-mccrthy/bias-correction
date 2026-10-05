"""Run MATLAB counterparts of the four paper experiments and compare outputs."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from eqtm import BiasCorrectionConfig
from eqtm.diagnostics import diagnosticunits
from eqtm.io import loadgriddata
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


def check_matlab() -> str:
    """Check that MATLAB can start before launching the paper experiments."""
    executable = shutil.which("matlab")
    if executable is None:
        raise RuntimeError("MATLAB must be on PATH to run the MATLAB-Python comparison.")
    subprocess.run(
        [executable, "-batch", "disp(['MATLAB available: ' version])"], check=True
    )
    return executable


def main(matlab_executable: str | None = None) -> None:
    """Reuse existing Python outputs, running one temporary MATLAB output at a time."""
    executable = matlab_executable or check_matlab()
    configs = [
        config_switzerland_tas_trends_on(),
        config_switzerland_tas_trends_off(),
        config_switzerland_pr_trends_on(),
        config_switzerland_pr_trends_off(),
    ]
    repo_root = Path(__file__).resolve().parents[2]
    paper_dir = repo_root / "paper" / "figures_and_tables"
    paper_dir.mkdir(parents=True, exist_ok=True)
    records_dir = Path(configs[0].file_path_bc_data).parent.parent / "matlab_python_comparison"
    records_dir.mkdir(parents=True, exist_ok=True)
    helper_dir = str(repo_root / "paper" / "scripts").replace("'", "''")
    rows = []

    for cfg in configs:
        python_output = Path(cfg.file_path_bc_data)
        if not python_output.is_file():
            raise FileNotFoundError(f"Run the Python paper experiment first: {python_output}")
        label = f"{cfg.clim_var_name}_trends_{'on' if cfg.trend_mapping else 'off'}"
        # Keep failed runs for inspection; remove only successfully compared NetCDFs.
        run_dir = Path(tempfile.mkdtemp(prefix=f"{label}_", dir=records_dir))
        matlab_output = run_dir / "matlab.nc"
        config_path = run_dir / "config.json"
        settings = asdict(cfg)
        settings["file_path_bc_data"] = str(matlab_output)
        settings["file_path_figures_tables"] = str(run_dir)
        config_path.write_text(json.dumps(settings, default=str, indent=2), encoding="utf-8")
        config_arg = str(config_path).replace("'", "''")
        command = f"addpath('{helper_dir}'); run_matlab_comparison('{config_arg}');"
        print(f"MATLAB-Python comparison: {label}; log: {run_dir / 'matlab.log'}", flush=True)
        with (run_dir / "matlab.log").open("w", encoding="utf-8") as log:
            subprocess.run(
                [executable, "-batch", command], stdout=log, stderr=subprocess.STDOUT,
                check=True,
            )
        rows.append(compare_outputs(cfg, matlab_output))
        table = pd.DataFrame(rows)
        table.to_csv(records_dir / "matlab_python_comparison.csv", index=False)
        table.to_csv(paper_dir / "matlab_python_comparison.csv", index=False)
        matlab_output.unlink()


def compare_outputs(cfg: BiasCorrectionConfig, matlab_output: Path) -> dict:
    """Compare full arrays in canonical y/x/time order, using double-precision differences."""
    python_grid = loadgriddata(cfg.file_path_bc_data, cfg.clim_var_name)
    try:
        matlab_grid = loadgriddata(matlab_output, cfg.clim_var_name)
        try:
            np.testing.assert_array_equal(python_grid.x, matlab_grid.x)
            np.testing.assert_array_equal(python_grid.y, matlab_grid.y)
            np.testing.assert_array_equal(python_grid.time, matlab_grid.time)
            np.testing.assert_equal(python_grid.clim_var.shape, matlab_grid.clim_var.shape)
            # Shared masked cells are allowed, but a missing value in only one output is an error.
            np.testing.assert_array_equal(
                np.isnan(python_grid.clim_var), np.isnan(matlab_grid.clim_var)
            )
            difference = np.subtract(
                python_grid.clim_var, matlab_grid.clim_var, dtype=np.float64
            )
            np.abs(difference, out=difference)
            if np.isinf(difference).any():
                raise ValueError("Non-finite differences found in MATLAB-Python comparison.")
            y, x, t = np.unravel_index(np.nanargmax(difference), difference.shape)
            return {
                "Variable": cfg.clim_var_name,
                "Trend mapping": "on" if cfg.trend_mapping else "off",
                "Units": diagnosticunits(cfg)[0],
                "Mean absolute difference": float(np.nanmean(difference)),
                "Maximum absolute difference": float(difference[y, x, t]),
                "X at maximum": float(python_grid.x[y, x]),
                "Y at maximum": float(python_grid.y[y, x]),
                "Time at maximum": str(python_grid.time[t]),
            }
        finally:
            matlab_grid.dataset.close()
    finally:
        python_grid.dataset.close()


if __name__ == "__main__":
    main()
