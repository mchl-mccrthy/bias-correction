import unittest

import numpy as np

from eqtm.spatial import getdistances, spatialmean


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


class TestSpatialMean(unittest.TestCase):
    def test_geographic_grid_uses_latitude_area_weights(self) -> None:
        grid_y = np.array([[0., 0.], [60., 60.]])
        grid = np.array([[0., 0.], [10., 10.]])

        self.assertAlmostEqual(spatialmean(grid, grid_y, "geographic"), 10 / 3)
        self.assertAlmostEqual(spatialmean(grid, grid_y, "projected"), 5.)

    def test_weights_are_renormalized_around_missing_cells(self) -> None:
        grid_y = np.array([[0., 0.], [60., 60.]])
        grid = np.array([[[0., np.nan], [0., np.nan]],
                         [[10., 10.], [10., 10.]]])

        np.testing.assert_allclose(
            spatialmean(grid, grid_y, "geographic"),
            [10 / 3, 10.],
        )


if __name__ == "__main__":
    unittest.main()
