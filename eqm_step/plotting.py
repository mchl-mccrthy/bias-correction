from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .config import BiasCorrectionConfig
from .diagnostics import Diagnostics, getoverlappingstationdata


def makeplots(diagnostics: Diagnostics, cfg: BiasCorrectionConfig) -> None:
    figure_dir = Path(cfg.file_path_figures)
    figure_dir.mkdir(parents=True, exist_ok=True)
    plotmaps(diagnostics, cfg, figure_dir)
    plottrendcomparison(diagnostics, cfg, figure_dir)
    plotallstationsqq(diagnostics, cfg, figure_dir)
    plotstationavailability(diagnostics, cfg, figure_dir)


def plotmaps(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    mean_grid = np.nanmean(diagnostics.bc_grid_clim_var_yearly, axis=2)
    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        mean_grid,
        "Long-term average",
        figure_dir / f"{cfg.clim_var_name}_long_term_average_map.png",
    )
    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        diagnostics.bc_grid_linear_trends,
        "Long-term trend",
        figure_dir / f"{cfg.clim_var_name}_bc_linear_trend_map.png",
    )


def plottrendcomparison(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    plt.figure(figsize=(4, 4))
    plt.scatter(diagnostics.station_linear_trends, diagnostics.raw_station_linear_trends, c="r", label="Raw")
    plt.scatter(diagnostics.station_linear_trends, diagnostics.bc_station_linear_trends, c="b", label="Bias corrected")
    plt.xlabel(f"{cfg.clim_var_long_name} trend, stations ({cfg.clim_var_units} yr$^{{-1}}$)")
    plt.ylabel(f"{cfg.clim_var_long_name} trend, gridded ({cfg.clim_var_units} yr$^{{-1}}$)")
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(figure_dir / f"{cfg.clim_var_name}_trend_comparison.png", dpi=300)
    plt.close()


def plotallstationsqq(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    plt.figure(figsize=(4, 4))
    qs = np.linspace(0, 1, 1000)
    qq_min = np.inf
    qq_max = -np.inf
    plotted = False
    for i_station in range(diagnostics.station_clim_var.shape[1]):
        station_overlap, raw_overlap, bc_overlap = getoverlappingstationdata(
            diagnostics.station_clim_var,
            diagnostics.raw_station_clim_var,
            diagnostics.bc_station_clim_var,
            diagnostics.station_time,
            diagnostics.grid_time,
            i_station,
        )
        if len(station_overlap) == 0:
            continue
        station_q = np.nanquantile(station_overlap, qs)
        raw_q = np.nanquantile(raw_overlap, qs)
        bc_q = np.nanquantile(bc_overlap, qs)
        plt.plot(station_q, raw_q, "r", alpha=0.6, label="Raw" if not plotted else None)
        plt.plot(station_q, bc_q, "b", alpha=0.6, label="Bias corrected" if not plotted else None)
        plotted = True
        qq_min = min(qq_min, np.nanmin(station_q), np.nanmin(raw_q), np.nanmin(bc_q))
        qq_max = max(qq_max, np.nanmax(station_q), np.nanmax(raw_q), np.nanmax(bc_q))
    if np.isfinite(qq_min) and np.isfinite(qq_max) and qq_min < qq_max:
        plt.xlim(qq_min, qq_max)
        plt.ylim(qq_min, qq_max)
    plt.xlabel(f"{cfg.clim_var_long_name}, station ({cfg.clim_var_units})")
    plt.ylabel(f"{cfg.clim_var_long_name}, gridded ({cfg.clim_var_units})")
    plt.title("All stations")
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(figure_dir / f"{cfg.clim_var_name}_all_stations_qq.png", dpi=300)
    plt.close()


def plotstationavailability(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    plt.figure(figsize=(5, 3))
    station_names = diagnostics.station_coords.get("station", diagnostics.station_clim_var.columns)
    for i_station, column in enumerate(diagnostics.station_clim_var.columns):
        valid = ~diagnostics.station_clim_var[column].isna()
        plt.scatter(diagnostics.station_time[valid], np.full(valid.sum(), i_station + 1), c="b", s=6)
        plt.text(diagnostics.station_time[-1], i_station + 1, str(station_names.iloc[i_station]), fontsize=7)
    plt.yticks([])
    plt.tight_layout()
    plt.savefig(figure_dir / f"{cfg.clim_var_name}_station_availability.png", dpi=300)
    plt.close()


def _map_figure(grid_x, grid_y, station_x, station_y, values, title: str, path: Path) -> None:
    plt.figure(figsize=(4, 4))
    plt.contourf(grid_x, grid_y, values, levels=100)
    plt.colorbar()
    plt.scatter(station_x, station_y, c="k", marker="*", label="Stations")
    plt.title(title)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
