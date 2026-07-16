from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import BiasCorrectionConfig, validateconfig
from .io import loadgriddata, loadstationdata, savebcdata
from .qmf import QMFs, getqmfs, period_index
from .spatial import getdistances, indexofclosest2
from .trends import detrendclimdata, gettrends, interptrends, retrendclimdata


@dataclass
class BiasCorrectionResults:
    write_output: bool
    file_path_bc_data: str
    mean_bc_grid_clim_var: float
    grid_biases: np.ndarray | None = None


def biascorrect(cfg: BiasCorrectionConfig) -> BiasCorrectionResults:
    print("Bias correcting climate data")
    validateconfig(cfg)

    station = loadstationdata(cfg.file_path_station_clim_var, cfg.file_path_station_coords)
    raw = loadgriddata(cfg.file_path_raw_data, cfg.clim_var_name)
    raw_grid_clim_var = raw.clim_var.copy()
    station_clim_var = station.clim_var.copy()

    if cfg.preserve_trends:
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
        cfg.idw_method,
        cfg.idw_alpha,
        keep_grid_biases=cfg.keep_grid_biases,
    )

    if cfg.preserve_trends:
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
            cfg.idw_method,
            cfg.idw_alpha,
        )
        bc_grid_clim_var = retrendclimdata(
            bc_grid_clim_var, station_grid_trends, cfg.bc_type, cfg.multiplicative_epsilon
        )

    if cfg.write_output:
        savebcdata(bc_grid_clim_var, cfg.file_path_raw_data, cfg.file_path_bc_data, cfg.clim_var_name)

    print("Bias correction completed")
    return BiasCorrectionResults(
        write_output=cfg.write_output,
        file_path_bc_data=str(cfg.file_path_bc_data),
        mean_bc_grid_clim_var=float(np.nanmean(bc_grid_clim_var)),
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
    idw_method: str,
    idw_alpha: float,
    keep_grid_biases: bool = False,
) -> tuple[np.ndarray, np.ndarray | None]:
    if bc_type == "multiplicative":
        with np.errstate(divide="ignore", invalid="ignore"):
            biases = qmfs.station_quantiles / qmfs.raw_quantiles
        biases[~np.isfinite(biases)] = 0
    elif bc_type == "additive":
        biases = qmfs.station_quantiles - qmfs.raw_quantiles
    else:
        raise ValueError("bc_type must be 'additive' or 'multiplicative'.")

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
        idw_method,
        idw_alpha,
    )
    rows, cols = indexofclosest2(station_x, station_y, raw_x, raw_y)
    station_lin_inds = np.ravel_multi_index((rows, cols), raw_x.shape)

    for i_time, time_value in enumerate(raw_time):
        bc_timestep, bias_timestep = mapquantilestimestep(
            raw_grid_clim_var[:, :, i_time],
            station_lin_inds,
            qmfs.raw_quantiles,
            biases,
            time_value,
            qmf_period,
            distances,
            raw_x,
            bc_type,
            idw_power,
        )
        bc_grid_clim_var[:, :, i_time] = bc_timestep
        if keep_grid_biases and grid_biases is not None:
            grid_biases[:, :, i_time] = bias_timestep

    return bc_grid_clim_var, grid_biases


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
    raw_station = raw_grid_clim_var_timestep.ravel()[station_lin_inds]
    i_period = period_index(raw_time_timestep, qmf_period)

    n_stations = len(station_lin_inds)
    station_biases = np.full(n_stations, np.nan)
    for i_station in range(n_stations):
        raw_q = raw_quantiles[:, i_station, i_period]
        if np.sum(~np.isnan(raw_q)) > 0:
            diff = np.abs(raw_station[i_station] - raw_q)
            quantile_index = np.nanargmin(diff)
            station_biases[i_station] = biases[quantile_index, i_station, i_period]

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
