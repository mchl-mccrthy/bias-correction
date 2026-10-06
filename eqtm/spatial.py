from __future__ import annotations

import numpy as np


def spatialmean(
    grid: np.ndarray,
    grid_y: np.ndarray,
    coordinate_system: str,
    chunk_size: int = 64,
) -> np.ndarray:
    """Area-weighted spatial mean over the first two grid dimensions."""
    grid = np.asarray(grid)
    grid_y = np.asarray(grid_y)
    if grid.shape[:2] != grid_y.shape:
        raise ValueError("grid_y must match the first two dimensions of grid.")
    if coordinate_system == "geographic":
        weights = np.cos(np.deg2rad(grid_y))
    elif coordinate_system == "projected":
        weights = np.ones_like(grid_y, dtype=float)
    else:
        raise ValueError("coordinate_system must be 'projected' or 'geographic'.")

    trailing_shape = grid.shape[2:]
    flat_grid = grid.reshape(np.prod(grid.shape[:2]), -1)
    flat_weights = weights.reshape(-1, 1)
    out = np.full(flat_grid.shape[1], np.nan, dtype=float)
    for start in range(0, flat_grid.shape[1], chunk_size):
        stop = min(start + chunk_size, flat_grid.shape[1])
        values = flat_grid[:, start:stop]
        valid = np.isfinite(values)
        numerator = np.sum(np.where(valid, values, 0.0) * flat_weights, axis=0)
        denominator = np.sum(valid * flat_weights, axis=0)
        np.divide(
            numerator,
            denominator,
            out=out[start:stop],
            where=denominator > 0,
        )
    result = out.reshape(trailing_shape)
    return result.item() if result.ndim == 0 else result


def getdistances(
    x1: np.ndarray,
    y1: np.ndarray,
    x2: np.ndarray,
    y2: np.ndarray,
    coordinate_system: str,
    z1: np.ndarray | None = None,
    z2: np.ndarray | None = None,
    idw_alpha: float = 0.0,
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

    if idw_alpha > 0:
        if z1 is None or z2 is None:
            raise ValueError(
                "cfg.idw_alpha > 0 requires elevation in both grid and station data."
            )
        dz = np.ravel(z1)[:, None] - np.ravel(z2)[None, :]
        d = np.sqrt(d**2 + (idw_alpha * dz) ** 2)

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
