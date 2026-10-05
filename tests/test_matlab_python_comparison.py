import tempfile
import unittest
import json
import os
import shutil
import subprocess
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from eqtm import biascorrect
from paper.scripts.compare_matlab_python import compare_outputs
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.cfg = replace(config_switzerland_tas_trends_on(), file_path_bc_data=root / "python.nc")
        self.matlab_path = root / "matlab.nc"
        self.data = xr.Dataset(
            {"tas": (("time", "lon", "lat"), np.ones((3, 2, 2), dtype=np.float32))},
            coords={"time": [0, 1, 2], "lon": [8.0, 9.0], "lat": [46.0, 47.0]},
        )
        self.data.time.attrs["units"] = "days since 2000-01-01"

    def test_difference_and_location_with_different_dimension_orders(self):
        self.data.to_netcdf(self.cfg.file_path_bc_data)
        other = self.data.copy(deep=True)
        other.tas.values[2, 1, 0] += 3
        other.transpose("lat", "time", "lon").to_netcdf(self.matlab_path)
        result = compare_outputs(self.cfg, self.matlab_path)
        self.assertEqual(result["Mean absolute difference"], 0.25)
        self.assertEqual(result["Maximum absolute difference"], 3.0)
        self.assertEqual(result["X at maximum"], 9.0)
        self.assertEqual(result["Y at maximum"], 46.0)
        self.assertEqual(result["Time at maximum"], "2000-01-03 00:00:00")

    def test_coordinate_mismatch_is_rejected(self):
        self.data.to_netcdf(self.cfg.file_path_bc_data)
        self.data.assign_coords(lon=[8.1, 9.1]).to_netcdf(self.matlab_path)
        with self.assertRaises(AssertionError):
            compare_outputs(self.cfg, self.matlab_path)

    def test_shared_missing_values_are_excluded(self):
        self.data.tas.values[0, 0, 0] = np.nan
        self.data.to_netcdf(self.cfg.file_path_bc_data)
        self.data.to_netcdf(self.matlab_path)
        result = compare_outputs(self.cfg, self.matlab_path)
        self.assertEqual(result["Mean absolute difference"], 0)

    def test_missing_value_mismatch_is_rejected(self):
        self.data.to_netcdf(self.cfg.file_path_bc_data)
        self.data.tas.values[0, 0, 0] = np.nan
        self.data.to_netcdf(self.matlab_path)
        with self.assertRaises(AssertionError):
            compare_outputs(self.cfg, self.matlab_path)

    @unittest.skipUnless(os.environ.get("EQTM_TEST_MATLAB") == "1", "Opt-in MATLAB integration test")
    def test_matlab_helper_for_all_four_configurations(self):
        root = Path(self.temp.name)
        times = pd.date_range("2000-01-01", periods=40)
        values = np.arange(160, dtype=np.float64).reshape(40, 2, 2) % 13 + 1
        coords = root / "stations.csv"
        pd.DataFrame({"station": ["A"], "lon": [8.2], "lat": [46.2]}).to_csv(coords, index=False)
        commands = []
        cases = []
        helper = Path(__file__).resolve().parents[1] / "paper" / "scripts"
        commands.append("addpath('" + str(helper).replace("'", "''") + "')")
        for variable, bc_type in [("tas", "additive"), ("pr", "multiplicative")]:
            raw_path = root / f"{variable}_raw.nc"
            ds = xr.Dataset(
                {variable: (("time", "lon", "lat"), values)},
                coords={"time": np.arange(40), "lon": [8., 9.], "lat": [46., 47.]},
            )
            ds.time.attrs["units"] = "days since 2000-01-01"
            ds.to_netcdf(raw_path)
            station_path = root / f"{variable}_station.csv"
            pd.DataFrame({"year": times.year, "month": times.month, "day": times.day,
                          "A": values[:, 0, 0] * 1.2 + 0.5}).to_csv(station_path, index=False)
            for trend_mapping in [True, False]:
                label = f"{variable}_{trend_mapping}"
                cfg = replace(
                    self.cfg, clim_var_name=variable, bc_type=bc_type,
                    trend_mapping=trend_mapping, trend_window=5, n_quantiles=11,
                    idw_alpha=0, use_parallel=False, n_workers=None,
                    file_path_raw_data=raw_path, file_path_station_coords=coords,
                    file_path_station_clim_var=station_path,
                    file_path_bc_data=root / f"{label}_python.nc",
                    file_path_figures_tables=root / "figures",
                )
                biascorrect(cfg)
                matlab_path = root / f"{label}_matlab.nc"
                config_path = root / f"{label}.json"
                config_path.write_text(json.dumps(asdict(replace(cfg, file_path_bc_data=matlab_path)),
                                                  default=str), encoding="utf-8")
                commands.append("run_matlab_comparison('" + str(config_path).replace("'", "''") + "')")
                cases.append((cfg, matlab_path))
        subprocess.run([shutil.which("matlab"), "-batch", ";".join(commands)], check=True)
        for cfg, matlab_path in cases:
            with self.subTest(variable=cfg.clim_var_name, trend_mapping=cfg.trend_mapping):
                result = compare_outputs(cfg, matlab_path)
                self.assertLess(result["Maximum absolute difference"], 1e-5)


if __name__ == "__main__":
    unittest.main()
