from pathlib import Path
import unittest

from eqtm.config import BiasCorrectionConfig
from eqtm.plotting import _format_units, _trend_units, _yearly_units


def _cfg(units: str, agg_method: str) -> BiasCorrectionConfig:
    return BiasCorrectionConfig(
        clim_var_name="test",
        clim_var_long_name="Test variable",
        clim_var_units=units,
        qmf_period="monthly",
        bc_type="additive",
        trend_mapping=True,
        trend_window=365,
        agg_method=agg_method,
        write_output=False,
        n_quantiles=101,
        idw_power=2,
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


class TestPlottingUnits(unittest.TestCase):
    def test_mean_units_keep_native_units_and_add_trend_year(self) -> None:
        cfg = _cfg("K", "mean")

        self.assertEqual(_yearly_units(cfg), "K")
        self.assertEqual(_trend_units(cfg), "K year$^{-1}$")

    def test_sum_units_add_year_denominators(self) -> None:
        cfg = _cfg("mm", "sum")

        self.assertEqual(_yearly_units(cfg), "mm year$^{-1}$")
        self.assertEqual(_trend_units(cfg), "mm year$^{-2}$")

    def test_sum_units_remove_terminal_daily_denominator(self) -> None:
        cfg = _cfg("kg m-2 day-1", "sum")

        self.assertEqual(_yearly_units(cfg), "kg m$^{-2}$ year$^{-1}$")
        self.assertEqual(_trend_units(cfg), "kg m$^{-2}$ year$^{-2}$")

    def test_braced_exponents_are_formatted(self) -> None:
        self.assertEqual(_format_units("kg m^{-2} day^{-1}"), "kg m$^{-2}$ day$^{-1}$")

    def test_braced_daily_denominator_is_removed_for_sum_units(self) -> None:
        cfg = _cfg("kg m^{-2} day^{-1}", "sum")

        self.assertEqual(_yearly_units(cfg), "kg m$^{-2}$ year$^{-1}$")
        self.assertEqual(_trend_units(cfg), "kg m$^{-2}$ year$^{-2}$")

    def test_existing_matplotlib_math_exponents_are_preserved(self) -> None:
        self.assertEqual(_format_units("kg m$^{-2}$ day$^{-1}$"), "kg m$^{-2}$ day$^{-1}$")

    def test_existing_matplotlib_daily_denominator_is_removed_for_sum_units(self) -> None:
        cfg = _cfg("kg m$^{-2}$ day$^{-1}$", "sum")

        self.assertEqual(_yearly_units(cfg), "kg m$^{-2}$ year$^{-1}$")
        self.assertEqual(_trend_units(cfg), "kg m$^{-2}$ year$^{-2}$")

    def test_degree_celsius_alias_is_formatted(self) -> None:
        self.assertEqual(_format_units("degC"), "°C")


if __name__ == "__main__":
    unittest.main()
