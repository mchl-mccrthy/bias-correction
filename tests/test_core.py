import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

from eqtm.config import BiasCorrectionConfig
from eqtm.core import biascorrect


class BiasCorrectTests(unittest.TestCase):
    @patch("eqtm.core.mapquantiles")
    @patch("eqtm.core.getqmfs")
    @patch("eqtm.core.loadgriddata")
    @patch("eqtm.core.loadstationdata")
    @patch("eqtm.core.validateconfig")
    def test_result_mean_uses_loaded_grid_latitudes(
        self,
        _validateconfig,
        loadstationdata,
        loadgriddata,
        getqmfs,
        mapquantiles,
    ):
        grid = np.array([[[0.0], [0.0]], [[10.0], [10.0]]])
        grid_x = np.array([[0.0, 1.0], [0.0, 1.0]])
        grid_y = np.array([[0.0, 0.0], [60.0, 60.0]])
        time = pd.DatetimeIndex(["2000-01-01"])

        loadstationdata.return_value = SimpleNamespace(
            clim_var=pd.DataFrame({"A": [1.0]}, index=time),
            x=np.array([0.0]),
            y=np.array([0.0]),
            z=None,
            time=time,
        )
        loadgriddata.return_value = SimpleNamespace(
            clim_var=grid,
            x=grid_x,
            y=grid_y,
            z=None,
            time=time,
        )
        getqmfs.return_value = SimpleNamespace()
        mapquantiles.return_value = (grid.copy(), None)

        cfg = BiasCorrectionConfig(
            clim_var_name="tas",
            clim_var_long_name="Temperature",
            clim_var_units="degC",
            qmf_period="whole",
            bc_type="additive",
            trend_mapping=False,
            trend_window=5,
            agg_method="mean",
            write_output=False,
            n_quantiles=11,
            idw_power=1,
            idw_alpha=0,
            use_parallel=False,
            n_workers=None,
            multiplicative_epsilon=0.1,
            keep_grid_biases=False,
            coordinate_system="geographic",
            file_path_station_coords="stations.csv",
            file_path_station_clim_var="tas.csv",
            file_path_raw_data="raw.nc",
            file_path_bc_data="corrected.nc",
            file_path_figures_tables="figures",
        )

        result = biascorrect(cfg)

        self.assertAlmostEqual(result.mean_bc_grid_clim_var, 10 / 3)


if __name__ == "__main__":
    unittest.main()
