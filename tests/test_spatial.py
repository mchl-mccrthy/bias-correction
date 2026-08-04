import unittest

import numpy as np

from eqtm.spatial import getdistances


class TestDistances(unittest.TestCase):
    def test_default_uses_horizontal_distance_without_elevation(self) -> None:
        distances = getdistances(
            np.array([3.0]),
            np.array([4.0]),
            np.array([0.0]),
            np.array([0.0]),
            "projected",
        )

        self.assertTrue(np.allclose(distances, [[5.0]]))

    def test_alpha_zero_uses_horizontal_distance_without_elevation(self) -> None:
        distances = getdistances(
            np.array([3.0]),
            np.array([4.0]),
            np.array([0.0]),
            np.array([0.0]),
            "projected",
            idw_alpha=0,
        )

        self.assertTrue(np.allclose(distances, [[5.0]]))

    def test_positive_alpha_adds_elevation_distance(self) -> None:
        distances = getdistances(
            np.array([3.0]),
            np.array([4.0]),
            np.array([0.0]),
            np.array([0.0]),
            "projected",
            np.array([1.0]),
            np.array([0.0]),
            idw_alpha=10,
        )

        self.assertTrue(np.allclose(distances, [[np.sqrt(125.0)]]))

    def test_positive_alpha_requires_elevation(self) -> None:
        with self.assertRaisesRegex(ValueError, "idw_alpha > 0"):
            getdistances(
                np.array([3.0]),
                np.array([4.0]),
                np.array([0.0]),
                np.array([0.0]),
                "projected",
                idw_alpha=10,
            )


if __name__ == "__main__":
    unittest.main()
