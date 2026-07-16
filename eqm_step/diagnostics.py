from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import BiasCorrectionConfig
from .io import loadgriddata, loadstationdata
from .spatial import indexofclosest2


@dataclass
class Diagnostics:
    """Diagnostic data used to evaluate and plot the bias-correction workflow."""

    station_clim_var: pd.DataFrame
    station_coords: pd.DataFrame
    station_x: np.ndarray
    station_y: np.ndarray
    station_time: pd.DatetimeIndex
    raw_station_clim_var: pd.DataFrame
    bc_station_clim_var: pd.DataFrame
    station_clim_var_yearly: pd.DataFrame
    raw_station_clim_var_yearly: pd.DataFrame
    bc_station_clim_var_yearly: pd.DataFrame
    years: np.ndarray
    station_linear_trends: np.ndarray
    raw_station_linear_trends: np.ndarray
    bc_station_linear_trends: np.ndarray
    bc_grid_clim_var_yearly: np.ndarray
    bc_grid_linear_trends: np.ndarray
    grid_x: np.ndarray
    grid_y: np.ndarray
    grid_time: pd.DatetimeIndex


def makediagnostics(cfg: BiasCorrectionConfig) -> Diagnostics:
    """Compute diagnostic summaries from raw, station, and corrected data.

    This function reloads the input and bias-corrected datasets, extracts raw
    and corrected grid values at station locations, creates annual station and
    grid summaries, and estimates linear trends for diagnostic plots.
    """

    if not Path(cfg.file_path_bc_data).is_file():
        raise FileNotFoundError(f"Bias-corrected data file not found: {cfg.file_path_bc_data}")

    raw = loadgriddata(cfg.file_path_raw_data, cfg.clim_var_name)
    bc = loadgriddata(cfg.file_path_bc_data, cfg.clim_var_name)
    station = loadstationdata(cfg.file_path_station_clim_var, cfg.file_path_station_coords)

    raw_station = gridtostations(raw.clim_var, station.x, station.y, raw.x, raw.y, station.clim_var)
    bc_station = gridtostations(bc.clim_var, station.x, station.y, raw.x, raw.y, station.clim_var)

    station_yearly, raw_station_yearly, bc_station_yearly, years = makeyearlytables(
        station.clim_var, raw_station, bc_station, raw.time, cfg.agg_method
    )
    station_trends, raw_trends, bc_trends = getlineartrends(
        station_yearly, raw_station_yearly, bc_station_yearly, years
    )
    bc_grid_yearly, grid_years = makeyearlygrid(bc.clim_var, raw.time, cfg.agg_method)
    bc_grid_trends = getgridlineartrends(bc_grid_yearly, grid_years)

    return Diagnostics(
        station.clim_var,
        station.coords,
        station.x,
        station.y,
        station.time,
        raw_station,
        bc_station,
        station_yearly,
        raw_station_yearly,
        bc_station_yearly,
        years,
        station_trends,
        raw_trends,
        bc_trends,
        bc_grid_yearly,
        bc_grid_trends,
        raw.x,
        raw.y,
        raw.time,
    )


def gridtostations(
    clim_var: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    template_table: pd.DataFrame,
) -> pd.DataFrame:
    rows, cols = indexofclosest2(station_x, station_y, grid_x, grid_y)
    out = pd.DataFrame(np.nan, index=template_table.index, columns=template_table.columns)
    for i_station in range(len(station_x)):
        out.iloc[:, i_station] = clim_var[rows[i_station], cols[i_station], :]
    return out


def makeyearlytables(
    station_clim_var: pd.DataFrame,
    raw_station_clim_var: pd.DataFrame,
    bc_station_clim_var: pd.DataFrame,
    grid_time: pd.DatetimeIndex,
    agg_method: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    min_year_completeness = 0.90
    years = np.unique(grid_time.year)
    yearly = [
        pd.DataFrame(np.nan, index=years, columns=station_clim_var.columns),
        pd.DataFrame(np.nan, index=years, columns=raw_station_clim_var.columns),
        pd.DataFrame(np.nan, index=years, columns=bc_station_clim_var.columns),
    ]

    for year in years:
        ind_year = grid_time.year == year
        for i_station, column in enumerate(station_clim_var.columns):
            station_tmp = station_clim_var.loc[ind_year, column].to_numpy()
            completeness = np.sum(~np.isnan(station_tmp)) / len(station_tmp)
            if completeness >= min_year_completeness:
                if agg_method == "sum":
                    reducer = np.nansum
                elif agg_method == "mean":
                    reducer = np.nanmean
                else:
                    raise ValueError("agg_method must be 'sum' or 'mean'.")
                yearly[0].loc[year, column] = reducer(station_clim_var.loc[ind_year, column])
                yearly[1].loc[year, column] = reducer(raw_station_clim_var.loc[ind_year, column])
                yearly[2].loc[year, column] = reducer(bc_station_clim_var.loc[ind_year, column])

    return yearly[0], yearly[1], yearly[2], years


def makeyearlygrid(
    grid_clim_var: np.ndarray,
    grid_time: pd.DatetimeIndex,
    agg_method: str,
) -> tuple[np.ndarray, np.ndarray]:
    years = np.unique(grid_time.year)
    yearly = np.full((*grid_clim_var.shape[:2], len(years)), np.nan, dtype=grid_clim_var.dtype)
    for i_year, year in enumerate(years):
        ind_year = grid_time.year == year
        if agg_method == "sum":
            yearly[:, :, i_year] = np.nansum(grid_clim_var[:, :, ind_year], axis=2)
        elif agg_method == "mean":
            yearly[:, :, i_year] = np.nanmean(grid_clim_var[:, :, ind_year], axis=2)
        else:
            raise ValueError("agg_method must be 'sum' or 'mean'.")
    return yearly, years


def getlineartrends(
    station_clim_var_yearly: pd.DataFrame,
    raw_station_clim_var_yearly: pd.DataFrame,
    bc_station_clim_var_yearly: pd.DataFrame,
    years: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_stations = station_clim_var_yearly.shape[1]
    station_trends = np.full(n_stations, np.nan)
    raw_trends = np.full(n_stations, np.nan)
    bc_trends = np.full(n_stations, np.nan)
    for i_station in range(n_stations):
        station_tmp = station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        raw_tmp = raw_station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        bc_tmp = bc_station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        valid = ~np.isnan(station_tmp) & ~np.isnan(raw_tmp) & ~np.isnan(bc_tmp)
        if np.sum(valid) >= 2:
            station_trends[i_station] = np.polyfit(years[valid], station_tmp[valid], 1)[0]
            raw_trends[i_station] = np.polyfit(years[valid], raw_tmp[valid], 1)[0]
            bc_trends[i_station] = np.polyfit(years[valid], bc_tmp[valid], 1)[0]
    return station_trends, raw_trends, bc_trends


def getgridlineartrends(grid_clim_var_yearly: np.ndarray, years: np.ndarray) -> np.ndarray:
    out = np.full(grid_clim_var_yearly.shape[:2], np.nan)
    for i_row in range(grid_clim_var_yearly.shape[0]):
        for i_col in range(grid_clim_var_yearly.shape[1]):
            grid_tmp = grid_clim_var_yearly[i_row, i_col, :]
            valid = ~np.isnan(grid_tmp)
            if np.sum(valid) >= 2:
                out[i_row, i_col] = np.polyfit(years[valid], grid_tmp[valid], 1)[0]
    return out


def getoverlappingstationdata(
    station_clim_var: pd.DataFrame,
    raw_station_clim_var: pd.DataFrame,
    bc_station_clim_var: pd.DataFrame,
    station_time: pd.DatetimeIndex,
    grid_time: pd.DatetimeIndex,
    i_station: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not station_time.equals(grid_time):
        raise ValueError("Station and grid time vectors must match exactly.")
    raw_overlap = raw_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    bc_overlap = bc_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    station_overlap = station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    valid = ~np.isnan(raw_overlap) & ~np.isnan(bc_overlap) & ~np.isnan(station_overlap)
    return station_overlap[valid], raw_overlap[valid], bc_overlap[valid]
