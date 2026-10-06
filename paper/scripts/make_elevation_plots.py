from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from eqtm.io import loadgridcoords, loadstationdata
from eqtm.plotting import (
    MARKER_SIZE,
    _new_figure,
    _save_figure,
    _set_plot_style,
    _trend_units,
    _yearly_units,
)
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on
from paper.scripts.diagnostics_cache import makediagnostics_cached as makediagnostics
from paper.scripts.make_maps import (
    _find_boundary_file,
    _load_switzerland_boundary,
    _mask_outside_switzerland,
)


GRID_COLOR = "0.65"
GRID_MARKER_SIZE = 0.8
GRID_ALPHA = 0.10


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures_and_tables"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()
    switzerland = _load_switzerland_boundary(_find_boundary_file(repo_root / "input_data" / "boundaries"))

    for make_config in (config_switzerland_tas_trends_on, config_switzerland_pr_trends_on):
        cfg = make_config()
        diagnostics = makediagnostics(cfg)
        grid_z = _load_grid_elevation(cfg)
        station_z = _load_station_elevation(cfg)

        _elevation_plot(
            grid_values=_grid_yearly_mean(diagnostics),
            station_values=_station_yearly_mean(diagnostics),
            grid_x=diagnostics.grid_x,
            grid_y=diagnostics.grid_y,
            grid_z=grid_z,
            station_z=station_z,
            switzerland=switzerland,
            x_label=f"{cfg.clim_var_long_name} ({_yearly_units(cfg)})",
            path=figure_dir / f"{cfg.clim_var_name}_elevation_mean.png",
        )
        _elevation_plot(
            grid_values=diagnostics.bc_grid_theil_sen_slopes,
            station_values=diagnostics.station_theil_sen_slopes,
            grid_x=diagnostics.grid_x,
            grid_y=diagnostics.grid_y,
            grid_z=grid_z,
            station_z=station_z,
            switzerland=switzerland,
            x_label=f"{cfg.clim_var_long_name} trend ({_trend_units(cfg)})",
            path=figure_dir / f"{cfg.clim_var_name}_elevation_trend.png",
        )


def _load_grid_elevation(cfg: BiasCorrectionConfig) -> np.ndarray:
    with xr.open_dataset(cfg.file_path_raw_data, decode_times=False) as ds:
        _, _, grid_z = loadgridcoords(ds)
    if grid_z is None:
        raise ValueError(f"Grid elevation not found in {cfg.file_path_raw_data}.")
    return grid_z


def _load_station_elevation(cfg: BiasCorrectionConfig) -> np.ndarray:
    station = loadstationdata(cfg.file_path_station_clim_var, cfg.file_path_station_coords)
    if station.z is None:
        raise ValueError(f"Station elevation not found in {cfg.file_path_station_coords}.")
    return station.z


def _station_yearly_mean(diagnostics: Diagnostics) -> np.ndarray:
    values = diagnostics.station_clim_var_yearly.to_numpy(dtype=float)
    valid = np.isfinite(values)
    sums = np.where(valid, values, 0).sum(axis=0)
    counts = valid.sum(axis=0)
    means = np.full(values.shape[1], np.nan)
    np.divide(sums, counts, out=means, where=counts > 0)
    return means


def _grid_yearly_mean(diagnostics: Diagnostics) -> np.ndarray:
    values = diagnostics.bc_grid_clim_var_yearly.astype(float, copy=False)
    valid = np.isfinite(values)
    sums = np.where(valid, values, 0).sum(axis=2)
    counts = valid.sum(axis=2)
    means = np.full(values.shape[:2], np.nan)
    np.divide(sums, counts, out=means, where=counts > 0)
    return means


def _elevation_plot(
    grid_values: np.ndarray,
    station_values: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    grid_z: np.ndarray,
    station_z: np.ndarray,
    switzerland,
    x_label: str,
    path: Path,
) -> None:
    grid_values = _mask_outside_switzerland(grid_x, grid_y, grid_values, switzerland)
    grid_z = _mask_outside_switzerland(grid_x, grid_y, grid_z, switzerland)
    fig, ax = _new_figure(3, 3, 4)
    valid_grid = np.isfinite(grid_values) & np.isfinite(grid_z)
    ax.scatter(
        grid_values[valid_grid],
        grid_z[valid_grid],
        color=GRID_COLOR,
        s=GRID_MARKER_SIZE,
        alpha=GRID_ALPHA,
        linewidths=0,
        zorder=0,
    )

    valid_stations = np.isfinite(station_values) & np.isfinite(station_z)
    ax.scatter(
        station_values[valid_stations],
        station_z[valid_stations],
        color="black",
        s=MARKER_SIZE,
        linewidths=0,
        zorder=3,
    )

    _set_limits(ax, grid_values, grid_z, station_values, station_z)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Elevation (m)")
    _save_figure(fig, path)


def _set_limits(
    ax,
    grid_values: np.ndarray,
    grid_z: np.ndarray,
    station_values: np.ndarray,
    station_z: np.ndarray,
) -> None:
    x_values = np.concatenate([np.ravel(grid_values), np.asarray(station_values, dtype=float)])
    y_values = np.concatenate([np.ravel(grid_z), np.asarray(station_z, dtype=float)])

    x_values = x_values[np.isfinite(x_values)]
    y_values = y_values[np.isfinite(y_values)]
    if x_values.size:
        x_span = np.nanmax(x_values) - np.nanmin(x_values)
        x_pad = 0.05 * x_span if x_span > 0 else 0.5
        ax.set_xlim(np.nanmin(x_values) - x_pad, np.nanmax(x_values) + x_pad)
    if y_values.size:
        y_span = np.nanmax(y_values) - np.nanmin(y_values)
        y_pad = 0.05 * y_span if y_span > 0 else 50
        ax.set_ylim(np.nanmin(y_values) - y_pad, np.nanmax(y_values) + y_pad)


if __name__ == "__main__":
    main()
