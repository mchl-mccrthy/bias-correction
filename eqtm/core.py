from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import os

import numpy as np

from .config import BiasCorrectionConfig, validateconfig
from .io import loadgriddata, loadstationdata, savebcdata
from .qmf import QMFs, getqmfs, period_index
from .spatial import getdistances, indexofclosest2, spatialmean
from .trends import detrendclimdata, gettrends, interptrends, retrendclimdata


_PARALLEL_MAP_STATE = None


@dataclass
class BiasCorrectionResults:
    """Summary returned by `biascorrect` after a correction run."""

    write_output: bool
    file_path_bc_data: str
    mean_bc_grid_clim_var: float
    grid_biases: np.ndarray | None = None


def biascorrect(cfg: BiasCorrectionConfig) -> BiasCorrectionResults:
    """Bias-correct gridded climate data using station observations.

    The workflow estimates empirical quantile-mapping corrections at station
    locations, interpolates those corrections to the grid with IDW, optionally
    maps station trends, and optionally writes a bias-corrected NetCDF
    file.

    Parameters
    ----------
    cfg
        Workflow configuration containing input paths, correction options,
    trend-mapping settings, interpolation settings, and output paths.

    Returns
    -------
    BiasCorrectionResults
        Summary of the run, including the output path, the mean corrected grid
        value, and optional interpolated bias grids.
    """

    print("Bias correcting climate data")
    validateconfig(cfg)

    station = loadstationdata(cfg.file_path_station_clim_var, cfg.file_path_station_coords)
    raw = loadgriddata(cfg.file_path_raw_data, cfg.clim_var_name)
    raw_grid_clim_var = raw.clim_var.copy()
    station_clim_var = station.clim_var.copy()

    if cfg.trend_mapping:
        raw_grid_trends = gettrends(raw_grid_clim_var, axis=2, window=cfg.trend_window)
        station_trends = gettrends(station_clim_var.to_numpy(dtype=float), axis=0, window=cfg.trend_window)
        raw_grid_clim_var = detrendclimdata(
            raw_grid_clim_var, raw_grid_trends, cfg.bc_type, cfg.multiplicative_epsilon
        )
        station_clim_var.iloc[:, :] = detrendclimdata(
            station_clim_var.to_numpy(dtype=float),
            station_trends,
            cfg.bc_type,
            cfg.multiplicative_epsilon,
        )

    qmfs = getqmfs(
        station_clim_var,
        station.x,
        station.y,
        station.time,
        raw_grid_clim_var,
        raw.x,
        raw.y,
        raw.time,
        cfg.qmf_period,
        cfg.n_quantiles,
    )

    bc_grid_clim_var, grid_biases = mapquantiles(
        raw_grid_clim_var,
        station.x,
        station.y,
        station.z,
        qmfs,
        raw.x,
        raw.y,
        raw.z,
        cfg.bc_type,
        cfg.qmf_period,
        raw.time,
        cfg.idw_power,
        cfg.coordinate_system,
        cfg.idw_alpha,
        use_parallel=cfg.use_parallel,
        n_workers=cfg.n_workers,
        keep_grid_biases=cfg.keep_grid_biases,
    )
    del raw_grid_clim_var

    if cfg.trend_mapping:
        station_grid_trends = interptrends(
            station_trends,
            station.x,
            station.y,
            station.z,
            raw.x,
            raw.y,
            raw.z,
            raw_grid_trends,
            cfg.bc_type,
            cfg.idw_power,
            cfg.coordinate_system,
            cfg.idw_alpha,
        )
        del raw_grid_trends
        bc_grid_clim_var = retrendclimdata(
            bc_grid_clim_var, station_grid_trends, cfg.bc_type, cfg.multiplicative_epsilon
        )
        del station_grid_trends

    if cfg.write_output:
        savebcdata(bc_grid_clim_var, cfg.file_path_raw_data, cfg.file_path_bc_data, cfg.clim_var_name, cfg)

    print("Bias correction completed")
    return BiasCorrectionResults(
        write_output=cfg.write_output,
        file_path_bc_data=str(cfg.file_path_bc_data),
        mean_bc_grid_clim_var=float(
            np.nanmean(spatialmean(bc_grid_clim_var, raw.y, cfg.coordinate_system))
        ),
        grid_biases=grid_biases,
    )


def mapquantiles(
    raw_grid_clim_var: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    station_z: np.ndarray | None,
    qmfs: QMFs,
    raw_x: np.ndarray,
    raw_y: np.ndarray,
    raw_z: np.ndarray | None,
    bc_type: str,
    qmf_period: str,
    raw_time,
    idw_power: float,
    coordinate_system: str,
    idw_alpha: float,
    use_parallel: bool = False,
    n_workers: int | None = None,
    keep_grid_biases: bool = False,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Map station quantile corrections to every grid cell and timestep.

    Station-level empirical quantile corrections are converted to timestep
    corrections and interpolated across the grid using inverse-distance
    weighting. Corrections are additive or multiplicative depending on
    `bc_type`. When parallel processing is enabled, timesteps are distributed
    among separate worker processes, equivalent to MATLAB's `parfor` loop.
    """

    biases = getquantilebiases(qmfs.station_quantiles, qmfs.raw_quantiles, bc_type)

    bc_grid_clim_var = np.full_like(raw_grid_clim_var, np.nan)
    grid_biases = np.full_like(raw_grid_clim_var, np.nan) if keep_grid_biases else None

    distances = getdistances(
        raw_x.ravel(),
        raw_y.ravel(),
        station_x,
        station_y,
        coordinate_system,
        None if raw_z is None else raw_z.ravel(),
        station_z,
        idw_alpha,
    )
    rows, cols = indexofclosest2(station_x, station_y, raw_x, raw_y)
    station_lin_inds = np.ravel_multi_index((rows, cols), raw_x.shape)

    def process_timestep(i_time: int) -> tuple[np.ndarray, np.ndarray]:
        return mapquantilestimestep(
            raw_grid_clim_var[:, :, i_time],
            station_lin_inds,
            qmfs.raw_quantiles,
            biases,
            raw_time[i_time],
            qmf_period,
            distances,
            raw_x,
            bc_type,
            idw_power,
        )

    n_timesteps = raw_grid_clim_var.shape[2]
    if use_parallel:
        state = (
            raw_grid_clim_var,
            station_lin_inds,
            qmfs.raw_quantiles,
            biases,
            raw_time,
            qmf_period,
            distances,
            raw_x,
            bc_type,
            idw_power,
            keep_grid_biases,
        )
        worker_count = min(n_workers or _availableworkers(), n_timesteps)
        chunksize = max(1, min(16, n_timesteps // (worker_count * 8)))
        with ProcessPoolExecutor(
            max_workers=worker_count,
            initializer=_initializemapworker,
            initargs=(state,),
        ) as executor:
            results = executor.map(_mapquantilesworker, range(n_timesteps), chunksize=chunksize)
            for i_time, (bc_timestep, bias_timestep) in enumerate(results):
                bc_grid_clim_var[:, :, i_time] = bc_timestep
                if keep_grid_biases and grid_biases is not None:
                    grid_biases[:, :, i_time] = bias_timestep
    else:
        for i_time in range(n_timesteps):
            bc_timestep, bias_timestep = process_timestep(i_time)
            bc_grid_clim_var[:, :, i_time] = bc_timestep
            if keep_grid_biases and grid_biases is not None:
                grid_biases[:, :, i_time] = bias_timestep

    return bc_grid_clim_var, grid_biases


def _availableworkers() -> int:
    """Return the CPUs available to this process, respecting scheduler affinity."""
    if hasattr(os, "sched_getaffinity"):
        return max(1, len(os.sched_getaffinity(0)))
    return max(1, os.cpu_count() or 1)


def _initializemapworker(state: tuple) -> None:
    """Store read-only mapping inputs once in each process worker."""
    global _PARALLEL_MAP_STATE
    _PARALLEL_MAP_STATE = state


def _mapquantilesworker(i_time: int) -> tuple[np.ndarray, np.ndarray | None]:
    """Map one timestep in a process worker, mirroring MATLAB's parfor loop."""
    if _PARALLEL_MAP_STATE is None:
        raise RuntimeError("Parallel quantile-mapping worker was not initialized.")
    (
        raw_grid_clim_var,
        station_lin_inds,
        raw_quantiles,
        biases,
        raw_time,
        qmf_period,
        distances,
        raw_x,
        bc_type,
        idw_power,
        keep_grid_biases,
    ) = _PARALLEL_MAP_STATE
    bc_timestep, bias_timestep = mapquantilestimestep(
        raw_grid_clim_var[:, :, i_time],
        station_lin_inds,
        raw_quantiles,
        biases,
        raw_time[i_time],
        qmf_period,
        distances,
        raw_x,
        bc_type,
        idw_power,
    )
    return bc_timestep, bias_timestep if keep_grid_biases else None


def getquantilebiases(
    station_quantiles: np.ndarray,
    raw_quantiles: np.ndarray,
    bc_type: str,
) -> np.ndarray:
    """Calculate additive or multiplicative station quantile corrections."""
    if bc_type == "multiplicative":
        with np.errstate(divide="ignore", invalid="ignore"):
            biases = station_quantiles / raw_quantiles
        # A zero model quantile cannot be adjusted multiplicatively. A factor
        # of one is neutral and avoids distorting the spatial interpolation.
        zero_denominator = (raw_quantiles == 0) & np.isfinite(station_quantiles)
        biases[zero_denominator] = 1
        return biases
    if bc_type == "additive":
        return station_quantiles - raw_quantiles
    raise ValueError("bc_type must be 'additive' or 'multiplicative'.")


def mapquantilestimestep(
    raw_grid_clim_var_timestep: np.ndarray,
    station_lin_inds: np.ndarray,
    raw_quantiles: np.ndarray,
    biases: np.ndarray,
    raw_time_timestep,
    qmf_period: str,
    distances: np.ndarray,
    grid_x: np.ndarray,
    bc_type: str,
    idw_power: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply interpolated station quantile corrections to one grid timestep."""

    raw_station = raw_grid_clim_var_timestep.ravel()[station_lin_inds]
    i_period = period_index(raw_time_timestep, qmf_period)

    n_stations = len(station_lin_inds)
    station_biases = np.full(n_stations, np.nan)
    for i_station in range(n_stations):
        raw_q = raw_quantiles[:, i_station, i_period]
        station_biases[i_station] = interpolatequantilebias(
            raw_station[i_station], raw_q, biases[:, i_station, i_period]
        )

    valid = np.isfinite(station_biases)
    d = distances[:, valid]
    b = station_biases[valid]
    weights = d ** (-idw_power)
    weights = weights / weights.sum(axis=1, keepdims=True)
    grid_biases = (weights @ b).reshape(grid_x.shape)

    if bc_type == "multiplicative":
        grid_biases[grid_biases < 0] = 0
        bc_timestep = grid_biases * raw_grid_clim_var_timestep
    else:
        bc_timestep = grid_biases + raw_grid_clim_var_timestep
    return bc_timestep, grid_biases


def interpolatequantilebias(
    raw_value: float,
    raw_quantiles: np.ndarray,
    quantile_biases: np.ndarray,
) -> float:
    """Interpolate a correction between adjacent empirical raw quantiles."""
    if not np.isfinite(raw_value):
        return np.nan

    raw_quantiles = np.asarray(raw_quantiles).reshape(-1)
    quantile_biases = np.asarray(quantile_biases).reshape(-1)
    valid = np.isfinite(raw_quantiles) & np.isfinite(quantile_biases)
    if not np.any(valid):
        return np.nan

    x = raw_quantiles[valid]
    corrections = quantile_biases[valid]

    # Empirical quantiles can repeat, particularly for zero precipitation.
    # Retaining the first correction preserves the existing lower-quantile
    # convention while giving interpolation distinct support points.
    keep = np.concatenate(([True], np.diff(x) != 0))
    x = x[keep]
    corrections = corrections[keep]

    if len(x) == 1 or raw_value <= x[0]:
        return float(corrections[0])
    if raw_value >= x[-1]:
        return float(corrections[-1])

    upper = int(np.searchsorted(x, raw_value, side="left"))
    if x[upper] == raw_value:
        return float(corrections[upper])
    lower = upper - 1
    fraction = (raw_value - x[lower]) / (x[upper] - x[lower])
    return float(corrections[lower] + fraction * (corrections[upper] - corrections[lower]))
