from pathlib import Path
import unittest

from eqtm.config import BiasCorrectionConfig
from eqtm.io import EQTM_REFERENCE, _eqtm_parameters


def _cfg() -> BiasCorrectionConfig:
    return BiasCorrectionConfig(
        clim_var_name="tas",
        clim_var_long_name="Temperature",
        clim_var_units="degC",
        qmf_period="monthly",
        bc_type="additive",
        trend_mapping=True,
        trend_window=1825,
        agg_method="mean",
        write_output=True,
        n_quantiles=201,
        idw_power=1,
        idw_alpha=10,
        multiplicative_epsilon=0.1,
        use_parallel=False,
        n_workers=None,
        keep_grid_biases=False,
        coordinate_system="geographic",
        file_path_station_coords=Path("station_coords.csv"),
        file_path_station_clim_var=Path("station_data.csv"),
        file_path_raw_data=Path("raw_data.nc"),
        file_path_bc_data=Path("bc_data.nc"),
        file_path_figures_tables=Path("figures_and_tables"),
    )


class TestOutputMetadata(unittest.TestCase):
    def test_eqtm_reference_points_to_repository(self) -> None:
        self.assertEqual(EQTM_REFERENCE, "https://github.com/mchl-mccrthy/bias-correction")

    def test_eqtm_parameters_include_core_settings(self) -> None:
        parameters = _eqtm_parameters(_cfg())

        self.assertIn("bc_type=additive", parameters)
        self.assertIn("qmf_period=monthly", parameters)
        self.assertIn("trend_mapping=true", parameters)
        self.assertIn("n_quantiles=201", parameters)
        self.assertIn("idw_power=1", parameters)
        self.assertIn("idw_alpha=10", parameters)
        self.assertIn("use_parallel=false", parameters)
        self.assertIn("n_workers=None", parameters)


if __name__ == "__main__":
    unittest.main()
