import unittest

import pandas as pd

from eqtm.io import matchstationcoords


class TestStationLoading(unittest.TestCase):
    def test_coordinates_are_matched_to_station_columns(self) -> None:
        station_clim_var = pd.DataFrame({"A": [1.0], "B": [2.0]})
        station_coords = pd.DataFrame(
            {
                "station": ["Unused", "B", "A"],
                "lat": [0.0, 20.0, 10.0],
                "lon": [0.0, 200.0, 100.0],
                "z": [0.0, 2.0, 1.0],
            }
        )

        matched = matchstationcoords(station_coords, station_clim_var.columns)

        self.assertEqual(list(matched["station"]), ["A", "B"])
        self.assertEqual(list(matched["lon"]), [100.0, 200.0])
        self.assertEqual(list(matched["lat"]), [10.0, 20.0])
        self.assertEqual(list(matched["z"]), [1.0, 2.0])

    def test_missing_station_coordinate_raises_error(self) -> None:
        station_clim_var = pd.DataFrame({"A": [1.0], "B": [2.0]})
        station_coords = pd.DataFrame(
            {
                "station": ["A"],
                "lat": [10.0],
                "lon": [100.0],
            }
        )

        with self.assertRaisesRegex(ValueError, "Station coordinates missing for: B"):
            matchstationcoords(station_coords, station_clim_var.columns)


if __name__ == "__main__":
    unittest.main()
