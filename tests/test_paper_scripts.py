import importlib
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
import pandas as pd

from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.cross_validation import _fold_export, _summarise
from paper.scripts.make_diagnostics_table import _diagnostics_table, METRIC_COLUMNS, ROW_LABELS


class PaperScriptTests(unittest.TestCase):
    def setUp(self):
        self.configs = [config_switzerland_tas_trends_on(), config_switzerland_pr_trends_on()]

    def test_all_script_modules_import_without_running_experiments(self):
        root = Path(__file__).resolve().parents[1] / "paper" / "scripts"
        for path in root.glob("*.py"):
            with self.subTest(module=path.stem):
                importlib.import_module(f"paper.scripts.{path.stem}")

    def check_headings(self, table):
        self.assertEqual(table.shape, (3, 6))
        self.assertEqual(list(table.index), ROW_LABELS)
        self.assertEqual(list(table.columns), [
            ("Temperature", "MAE quantiles (\N{DEGREE SIGN}C)"),
            ("Temperature", "MAE yearly (\N{DEGREE SIGN}C)"),
            ("Temperature", "MAE trends (\N{DEGREE SIGN}C year^-1)"),
            ("Precipitation", "MAE quantiles (mm day^-1)"),
            ("Precipitation", "MAE yearly (mm year^-1)"),
            ("Precipitation", "MAE trends (mm year^-2)"),
        ])
        recovered = pd.read_csv(StringIO(table.to_csv()), header=[0, 1], index_col=0)
        pd.testing.assert_frame_equal(recovered, table, check_dtype=False)

    def test_in_sample_summary_units_and_values(self):
        times = pd.date_range("2000-01-01", periods=2)
        def diagnostics(bias):
            table = pd.DataFrame([[1., 2., 3.], [bias, bias + 1, bias + 2]], columns=METRIC_COLUMNS)
            table["Dataset"] = ["Raw", "Bias-corrected"]
            return SimpleNamespace(summary_table=table, station_time=times,
                                   grid_time=times, years=np.array([2000]))
        table = _diagnostics_table(self.configs[0], diagnostics(4), diagnostics(7),
                                   self.configs[1], diagnostics(4), diagnostics(7))
        self.check_headings(table)
        np.testing.assert_equal(table.iloc[:, :3].to_numpy(), [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_cross_validation_summary_and_fold_units(self):
        rows = []
        for cfg in self.configs:
            for method in ROW_LABELS:
                for fold in [1, 2]:
                    rows.append({"Variable": cfg.clim_var_name, "Method": method,
                                 "Station": str(fold), "Fold": fold,
                                 "MAE quantiles": fold, "MAE yearly": 2 * fold,
                                 "MAE trends": 3 * fold,
                                 "Station trend": -fold, "Model trend": 2 * fold})
        folds = pd.DataFrame(rows)
        table = _summarise(folds, self.configs)
        self.check_headings(table)
        np.testing.assert_allclose(table.iloc[0].to_numpy(), [1.5, 3, 4.5] * 2)
        exported = _fold_export(folds, self.configs)
        self.assertIn("AE trend", exported)
        self.assertNotIn("MAE trends", exported)
        for variable, expected in [("tas", ["\N{DEGREE SIGN}C", "\N{DEGREE SIGN}C", "\N{DEGREE SIGN}C year^-1"]),
                                   ("pr", ["mm day^-1", "mm year^-1", "mm year^-2"])]:
            actual = exported.loc[exported.Variable == variable,
                                  ["Quantile units", "Yearly units", "Trend units"]].iloc[0].tolist()
            self.assertEqual(actual, expected)
        pd.testing.assert_series_equal(
            exported["AE trend"], folds["MAE trends"], check_names=False
        )


if __name__ == "__main__":
    unittest.main()
