from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from eqtm.diagnostics import diagnosticcsvtable, getdomainsummary, getstationmeans, makediagnostics, makesummarytable
from scripts.config_andermatt_zurich_tas import config_andermatt_zurich_tas


class DiagnosticTableTests(unittest.TestCase):
    def test_means_use_same_valid_years(self):
        station = pd.DataFrame({"A": [1., np.nan, 3.], "B": [np.nan] * 3})
        raw = pd.DataFrame({"A": [2., 100., np.nan], "B": [10.] * 3})
        bc = pd.DataFrame({"A": [1.5, 100., 5.], "B": [10.] * 3})
        means = getstationmeans(station, raw, bc)
        for actual, expected in zip(means, [1., 2., 1.5]):
            np.testing.assert_allclose(actual, [expected, np.nan])

    def test_summary_preserves_signed_trends_and_averages_absolute_errors(self):
        data = [np.array(x) for x in (
            [1., 3.], [-1., 5.], [1., 3.], [2., 4.], [0., 0.],
            [3., 5.], [0., 0.], [10., 20.], [12., 24.], [10., 20.],
        )]
        summary = makesummarytable("tas", *data)
        self.assertEqual(summary.loc[0, "Observed mean"], 15.)
        self.assertEqual(summary.loc[0, "Model mean"], 18.)
        self.assertEqual(summary.loc[0, "Observed linear trend"], 2.)
        self.assertEqual(summary.loc[0, "Model linear trend"], 2.)
        self.assertEqual(summary.loc[0, "MAE linear trends"], 2.)
        self.assertEqual(summary.loc[1, "MAE linear trends"], 0.)

    def test_makediagnostics_writes_station_and_overview_csvs(self):
        for aggregation, units in [("mean", "degC"), ("sum", "mm day^{-1}")]:
            with self.subTest(aggregation=aggregation):
                self.check_csvs(aggregation, units)

    def test_domain_summary_missing_years(self):
        grid = np.array([[[1., np.nan, 5.]], [[3., np.nan, 7.]]])
        with self.assertWarns(RuntimeWarning):
            mean, trend = getdomainsummary(grid, np.array([2000, 2001, 2002]))
        self.assertEqual(mean, 4.)
        self.assertAlmostEqual(trend, 2.)

    def check_csvs(self, aggregation, units):
        time = pd.date_range("2000-01-01", "2002-12-31")
        observed = (time.year - 1999).to_numpy(dtype=float)
        stations = pd.DataFrame({"ALT": observed, "SMA": observed + 10})
        x, y = np.meshgrid([8., 9.], [46., 47.])
        raw_values = np.broadcast_to(observed + 2, (2, 2, len(time))).copy()
        raw_values[:, 1, :] += 10
        raw_values[1, :, :] += 20 * observed  # Unsampled cells must affect domain statistics.
        raw = SimpleNamespace(clim_var=raw_values, x=x, y=y, time=time)
        bc = SimpleNamespace(clim_var=raw_values - 1)
        station = SimpleNamespace(
            clim_var=stations, x=np.array([8., 9.]), y=np.array([46., 46.]),
            coords=pd.DataFrame({"station": ["ALT", "SMA"]}), time=time,
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            existing_output = root / "existing.nc"
            existing_output.touch()
            cfg = replace(config_andermatt_zurich_tas(), file_path_bc_data=existing_output,
                          file_path_figures_tables=root, agg_method=aggregation, clim_var_units=units)
            with patch("eqtm.diagnostics.loadgriddata", side_effect=[raw, bc]), \
                    patch("eqtm.diagnostics.loadstationdata", return_value=station):
                diagnostics = makediagnostics(cfg)
            overview = pd.read_csv(root / "overview" / "tas_diagnostics_summary.csv")
            pd.testing.assert_frame_equal(overview, diagnosticcsvtable(diagnostics.summary_table, cfg))
            yearly_unit = "\N{DEGREE SIGN}C" if aggregation == "mean" else "mm year^-1"
            trend_unit = "\N{DEGREE SIGN}C year^-1" if aggregation == "mean" else "mm year^-2"
            native_unit = "\N{DEGREE SIGN}C" if aggregation == "mean" else "mm day^-1"
            self.assertIn(f"MAE quantiles ({native_unit})", overview)
            self.assertFalse(any("Observed" in column for column in overview))
            annual = np.array([np.mean(observed[time.year == year]) if aggregation == "mean"
                               else np.sum(observed[time.year == year]) for year in [2000, 2001, 2002]])
            days = np.ones(3) if aggregation == "mean" else np.array([366, 365, 365])
            domain_raw = 11 * annual + 7 * days
            np.testing.assert_allclose(overview[f"Domain mean yearly ({yearly_unit})"],
                                       [domain_raw.mean(), (domain_raw - days).mean()])
            np.testing.assert_allclose(overview[f"Domain linear trend ({trend_unit})"],
                                       [np.polyfit([2000, 2001, 2002], series, 1)[0]
                                        for series in [domain_raw, domain_raw - days]])
            for name in ["ALT", "SMA"]:
                table = pd.read_csv(root / "individual_stations" / f"{name}_tas_diagnostics_summary.csv")
                self.assertEqual(list(table.Dataset), ["Raw", "Bias-corrected"])
                self.assertEqual(list(table.Station), [name, name])
                self.assertIn(f"AE linear trend ({trend_unit})", table.columns)
                self.assertNotIn("MAE linear trends", table.columns)
                offset = 0 if name == "ALT" else 10
                np.testing.assert_allclose(table[f"Observed mean yearly ({yearly_unit})"],
                                           (annual + offset * days).mean())
                np.testing.assert_allclose(table[f"Model mean yearly ({yearly_unit})"],
                                           [(annual + (offset + bias) * days).mean() for bias in [2, 1]])


if __name__ == "__main__":
    unittest.main()
