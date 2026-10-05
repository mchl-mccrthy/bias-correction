from dataclasses import replace
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from eqtm.config import validateconfig
from eqtm.core import mapquantiles
from eqtm.qmf import QMFs
from scripts.config_andermatt_zurich_tas import config_andermatt_zurich_tas


class ParallelTests(unittest.TestCase):
    def setUp(self):
        self.raw = np.arange(24, dtype=float).reshape(2, 2, 6)
        self.x, self.y = np.meshgrid([0., 1.], [0., 1.])
        self.station_x = np.array([0., 1.])
        self.station_y = np.array([0., 1.])
        probabilities = np.array([0., 0.5, 1.])
        raw_quantiles = np.array([[[0.], [1.]], [[8.], [9.]], [[20.], [21.]]])
        station_quantiles = raw_quantiles + np.array([[[1., 2.]]]).reshape(1, 2, 1)
        self.qmfs = QMFs(probabilities, station_quantiles, raw_quantiles)
        self.time = pd.date_range("2000-01-01", periods=6)

    def run_mapping(self, use_parallel, n_workers, keep_grid_biases=True):
        return mapquantiles(
            self.raw, self.station_x, self.station_y, None, self.qmfs,
            self.x, self.y, None, "additive", "whole", self.time, 1,
            "projected", 0, use_parallel=use_parallel, n_workers=n_workers,
            keep_grid_biases=keep_grid_biases,
        )

    def test_parallel_and_serial_results_match(self):
        serial = self.run_mapping(False, None)
        parallel = self.run_mapping(True, 2)
        parallel_without_biases = self.run_mapping(True, 2, keep_grid_biases=False)
        np.testing.assert_array_equal(parallel[0], serial[0])
        np.testing.assert_array_equal(parallel[1], serial[1])
        np.testing.assert_array_equal(parallel_without_biases[0], serial[0])
        self.assertIsNone(parallel_without_biases[1])

    def test_parallel_configuration_validation(self):
        cfg = config_andermatt_zurich_tas()
        with patch.object(Path, "is_file", return_value=True):
            validateconfig(replace(cfg, use_parallel=True, n_workers=2))
            for invalid in (0, -1, 1.5, True):
                with self.subTest(n_workers=invalid):
                    with self.assertRaisesRegex(ValueError, "n_workers"):
                        validateconfig(replace(cfg, use_parallel=True, n_workers=invalid))
            with self.assertRaisesRegex(ValueError, "use_parallel"):
                validateconfig(replace(cfg, use_parallel=1))


if __name__ == "__main__":
    unittest.main()
