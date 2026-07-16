from __future__ import annotations

import numpy as np


def getdistances(
    x1: np.ndarray,
    y1: np.ndarray,
    x2: np.ndarray,
    y2: np.ndarray,
    coordinate_system: str,
    z1: np.ndarray | None = None,
    z2: np.ndarray | None = None,
    idw_method: str = "horizontal",
    idw_alpha: float = 10.0,
) -> np.ndarray:
    if coordinate_system == "projected":
        d = np.sqrt((np.ravel(x1)[:, None] - np.ravel(x2)[None, :]) ** 2 +
                    (np.ravel(y1)[:, None] - np.ravel(y2)[None, :]) ** 2)
    elif coordinate_system == "geographic":
        earth_radius_m = 6_371_000.0
        lon1 = np.deg2rad(np.ravel(x1))[:, None]
        lat1 = np.deg2rad(np.ravel(y1))[:, None]
        lon2 = np.deg2rad(np.ravel(x2))[None, :]
        lat2 = np.deg2rad(np.ravel(y2))[None, :]
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        d = 2 * earth_radius_m * np.arcsin(np.sqrt(a))
    else:
        raise ValueError("coordinate_system must be 'projected' or 'geographic'.")

    if idw_method == "elevation_aware":
        if z1 is None or z2 is None:
            raise ValueError(
                "cfg.idw_method = elevation_aware requires elevation in both grid and station data."
            )
        dz = np.ravel(z1)[:, None] - np.ravel(z2)[None, :]
        d = np.sqrt(d**2 + (idw_alpha * dz) ** 2)
    elif idw_method != "horizontal":
        raise ValueError("idw_method must be 'horizontal' or 'elevation_aware'.")

    d[d == 0] = np.finfo(float).eps
    return d


def indexofclosest2(xq: np.ndarray, yq: np.ndarray, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    query = np.column_stack([np.ravel(xq), np.ravel(yq)])
    grid = np.column_stack([x.ravel(), y.ravel()])
    dist2 = ((query[:, None, :] - grid[None, :, :]) ** 2).sum(axis=2)
    flat_index = np.argmin(dist2, axis=1)
    return np.unravel_index(flat_index, x.shape)


def idw_interpolate(distances: np.ndarray, values: np.ndarray, idw_power: float) -> np.ndarray:
    valid = np.isfinite(values)
    if not np.any(valid):
        return np.full(distances.shape[0], np.nan)
    d = distances[:, valid]
    v = values[valid]
    weights = d ** (-idw_power)
    weights = weights / weights.sum(axis=1, keepdims=True)
    return weights @ v
