from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .spatial import indexofclosest2


@dataclass
class QMFs:
    probabilities: np.ndarray
    station_quantiles: np.ndarray
    raw_quantiles: np.ndarray


def getqmf(station_clim_var: np.ndarray, raw_clim_var: np.ndarray, n_quantiles: int) -> dict[str, np.ndarray]:
    station_values = np.asarray(station_clim_var, dtype=float).copy()
    raw_values = np.asarray(raw_clim_var, dtype=float).copy()
    make_nan = np.isnan(raw_values) | np.isnan(station_values)
    raw_values[make_nan] = np.nan
    station_values[make_nan] = np.nan

    qs = np.linspace(0, 1, n_quantiles)
    return {
        "probabilities": qs,
        "station_quantiles": np.nanquantile(station_values, qs, method="hazen"),
        "raw_quantiles": np.nanquantile(raw_values, qs, method="hazen"),
    }


def getqmfs(
    station_clim_var: pd.DataFrame,
    station_x: np.ndarray,
    station_y: np.ndarray,
    station_time: pd.DatetimeIndex,
    raw_clim_var: np.ndarray,
    raw_x: np.ndarray,
    raw_y: np.ndarray,
    raw_time: pd.DatetimeIndex,
    qmf_period: str,
    n_quantiles: int,
) -> QMFs:
    if not station_time.equals(raw_time):
        raise ValueError("Station and grid time vectors must match exactly.")

    periods = _periods(qmf_period)
    n_stations = len(station_x)
    n_periods = len(periods)
    probabilities = np.linspace(0, 1, n_quantiles)
    station_quantiles = np.full((n_quantiles, n_stations, n_periods), np.nan)
    raw_quantiles = np.full((n_quantiles, n_stations, n_periods), np.nan)

    rows, cols = indexofclosest2(station_x, station_y, raw_x, raw_y)
    for i_station in range(n_stations):
        station_values = station_clim_var.iloc[:, i_station].to_numpy()
        raw_station_values = raw_clim_var[rows[i_station], cols[i_station], :]
        for i_period, period in enumerate(periods):
            cond = _period_mask(raw_time, qmf_period, period)
            qmf = getqmf(station_values[cond], raw_station_values[cond], n_quantiles)
            station_quantiles[:, i_station, i_period] = qmf["station_quantiles"]
            raw_quantiles[:, i_station, i_period] = qmf["raw_quantiles"]

    return QMFs(probabilities, station_quantiles, raw_quantiles)


def period_index(time_value: pd.Timestamp, qmf_period: str) -> int:
    if qmf_period == "whole":
        return 0
    if qmf_period == "seasonal":
        return (time_value.month % 12) // 3
    if qmf_period == "monthly":
        return time_value.month - 1
    raise ValueError("qmf_period must be 'whole', 'seasonal', or 'monthly'.")


def _periods(qmf_period: str) -> list[int]:
    if qmf_period == "whole":
        return [1]
    if qmf_period == "seasonal":
        return [1, 2, 3, 4]
    if qmf_period == "monthly":
        return list(range(1, 13))
    raise ValueError("qmf_period must be 'whole', 'seasonal', or 'monthly'.")


def _period_mask(time: pd.DatetimeIndex, qmf_period: str, period: int) -> np.ndarray:
    if qmf_period == "whole":
        return np.ones(len(time), dtype=bool)
    if qmf_period == "seasonal":
        seasons = (time.month % 12) // 3 + 1
        return seasons == period
    if qmf_period == "monthly":
        return time.month == period
    raise ValueError("qmf_period must be 'whole', 'seasonal', or 'monthly'.")
