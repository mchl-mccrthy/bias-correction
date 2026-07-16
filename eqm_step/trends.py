from __future__ import annotations

import numpy as np
import pandas as pd

from .spatial import getdistances, idw_interpolate, indexofclosest2


def gettrends(clim_data: np.ndarray, axis: int, window: int) -> np.ndarray:
    moved = np.moveaxis(clim_data, axis, 0)
    flat = moved.reshape(moved.shape[0], -1)
    trend = (
        pd.DataFrame(flat)
        .rolling(window=window, min_periods=1, center=True)
        .mean()
        .to_numpy()
    )
    return np.moveaxis(trend.reshape(moved.shape), 0, axis)


def detrendclimdata(clim_data: np.ndarray, trends: np.ndarray, bc_type: str, multiplicative_epsilon: float) -> np.ndarray:
    if bc_type == "additive":
        return clim_data - trends
    return (clim_data + multiplicative_epsilon) / (trends + multiplicative_epsilon)


def retrendclimdata(clim_data: np.ndarray, trends: np.ndarray, bc_type: str, multiplicative_epsilon: float) -> np.ndarray:
    if bc_type == "additive":
        return clim_data + trends
    out = clim_data * (trends + multiplicative_epsilon) - multiplicative_epsilon
    valid = ~np.isnan(out)
    out[valid] = np.maximum(out[valid], 0)
    return out


def interptrends(
    station_trends: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    station_z: np.ndarray | None,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    grid_z: np.ndarray | None,
    grid_trends: np.ndarray,
    bc_type: str,
    idw_power: float,
    coordinate_system: str,
    idw_method: str,
    idw_alpha: float,
) -> np.ndarray:
    n_timesteps = station_trends.shape[0]
    out = np.zeros((*grid_x.shape, n_timesteps))
    rows, cols = indexofclosest2(station_x, station_y, grid_x, grid_y)
    distances = getdistances(
        grid_x.ravel(),
        grid_y.ravel(),
        station_x,
        station_y,
        coordinate_system,
        None if grid_z is None else grid_z.ravel(),
        station_z,
        idw_method,
        idw_alpha,
    )

    for i_time in range(n_timesteps):
        grid_at_stations = grid_trends[rows, cols, i_time]
        stn_vals = station_trends[i_time, :]
        if bc_type == "additive":
            corr_vals = stn_vals - grid_at_stations
            corr_vals[~np.isfinite(corr_vals)] = 0
        else:
            corr_vals = stn_vals / grid_at_stations
            corr_vals[~np.isfinite(corr_vals)] = 1
        corr_grid = idw_interpolate(distances, corr_vals, idw_power).reshape(grid_x.shape)
        if bc_type == "additive":
            out[:, :, i_time] = grid_trends[:, :, i_time] + corr_grid
        else:
            out[:, :, i_time] = grid_trends[:, :, i_time] * corr_grid
    return out
