import unittest

import numpy as np

from eqtm.core import interpolatequantilebias


class QuantileInterpolationTests(unittest.TestCase):
    def test_interpolates_between_adjacent_quantiles(self):
        result = interpolatequantilebias(5.0, [0.0, 10.0, 20.0], [1.0, 3.0, 9.0])
        self.assertEqual(result, 2.0)

    def test_uses_exact_quantile_correction(self):
        result = interpolatequantilebias(10.0, [0.0, 10.0, 20.0], [1.0, 3.0, 9.0])
        self.assertEqual(result, 3.0)

    def test_clamps_values_to_endpoint_corrections(self):
        self.assertEqual(interpolatequantilebias(-1.0, [0.0, 10.0], [2.0, 4.0]), 2.0)
        self.assertEqual(interpolatequantilebias(11.0, [0.0, 10.0], [2.0, 4.0]), 4.0)

    def test_repeated_quantiles_retain_first_correction(self):
        self.assertEqual(interpolatequantilebias(0.0, [0.0, 0.0, 10.0], [1.0, 4.0, 5.0]), 1.0)
        self.assertEqual(interpolatequantilebias(5.0, [0.0, 0.0, 10.0], [1.0, 4.0, 5.0]), 3.0)

    def test_ignores_invalid_quantile_correction_pairs(self):
        result = interpolatequantilebias(5.0, [0.0, np.nan, 10.0], [1.0, 99.0, 3.0])
        self.assertEqual(result, 2.0)

    def test_returns_nan_without_a_usable_mapping(self):
        self.assertTrue(np.isnan(interpolatequantilebias(np.nan, [0.0], [1.0])))
        self.assertTrue(np.isnan(interpolatequantilebias(1.0, [np.nan], [np.nan])))

    def test_single_quantile_uses_its_correction(self):
        self.assertEqual(interpolatequantilebias(5.0, [2.0], [7.0]), 7.0)


if __name__ == "__main__":
    unittest.main()
