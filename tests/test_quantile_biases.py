import unittest

import numpy as np

from eqtm.core import getquantilebiases


class QuantileBiasTests(unittest.TestCase):
    def test_zero_denominators_use_neutral_multiplicative_factor(self):
        station = np.array([0., 2., np.nan, 0., 6.])
        raw = np.array([0., 0., np.nan, 2., 3.])

        actual = getquantilebiases(station, raw, "multiplicative")

        np.testing.assert_allclose(actual, [1., 1., np.nan, 0., 2.], equal_nan=True)

    def test_additive_biases_are_unchanged(self):
        station = np.array([0., 2., np.nan])
        raw = np.array([0., 1., np.nan])

        actual = getquantilebiases(station, raw, "additive")

        np.testing.assert_allclose(actual, [0., 1., np.nan], equal_nan=True)

    def test_unknown_bias_correction_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "bc_type"):
            getquantilebiases(np.array([1.]), np.array([1.]), "unknown")


if __name__ == "__main__":
    unittest.main()
