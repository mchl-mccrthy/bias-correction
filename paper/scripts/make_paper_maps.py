from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import numpy as np
import shapely

from eqtm import makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from eqtm.plotting import (
    BOX_LINE_WIDTH,
    CM_TO_IN,
    FONT_SIZE,
    MIN_TICKS,
    TICK_LENGTH_POINTS,
    _set_plot_style,
    _trend_units,
    _yearly_units,
)
from paper.scripts.make_paper_locator_map import _find_boundary_file, _load_switzerland_boundary
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


MAX_COLORBAR_TICKS = 4
PLOT_WIDTH_CM = 7.5
MARGIN_CM = 2
COLORBAR_WIDTH_CM = 0.25
COLORBAR_GAP_CM = 0.35
STATION_MARKER_SIZE = 10
CENTERED_CMAP = "RdBu_r"
PRECIPITATION_CMAP = "turbo"
TEMPERATURE_CMAP = "RdBu_r"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures_and_tables"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()
    switzerland = _load_switzerland_boundary(_find_boundary_file(repo_root / "input_data" / "boundaries"))

    map_specs = [
        (config_switzerland_tas_trends_on(), "mean"),
        (config_switzerland_pr_trends_on(), "mean"),
        (config_switzerland_tas_trends_on(), "trend"),
        (config_switzerland_pr_trends_on(), "trend"),
    ]

    diagnostics_cache: dict[str, Diagnostics] = {}
    for cfg, map_type in map_specs:
        diagnostics = diagnostics_cache.setdefault(cfg.clim_var_name, makediagnostics(cfg))
        _paper_map(diagnostics, cfg, map_type, switzerland, figure_dir)


def _paper_map(
    diagnostics: Diagnostics,
    cfg: BiasCorrectionConfig,
    map_type: str,
    switzerland: gpd.GeoDataFrame,
    figure_dir: Path,
) -> None:
    if map_type == "mean":
        values = np.nanmean(diagnostics.bc_grid_clim_var_yearly, axis=2)
        colorbar_label = _mean_label(cfg)
        file_name = f"{cfg.clim_var_name}_long_term_average_map.png"
    elif map_type == "trend":
        values = diagnostics.bc_grid_linear_trends
        colorbar_label = _trend_label(cfg)
        file_name = f"{cfg.clim_var_name}_linear_trend_map.png"
    else:
        raise ValueError("map_type must be 'mean' or 'trend'.")

    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        values,
        colorbar_label,
        cfg.coordinate_system,
        cfg.clim_var_name,
        map_type,
        switzerland,
        figure_dir / file_name,
    )


def _mean_label(cfg: BiasCorrectionConfig) -> str:
    return f"{cfg.clim_var_long_name} ({_yearly_units(cfg)})"


def _trend_label(cfg: BiasCorrectionConfig) -> str:
    return f"{cfg.clim_var_long_name} trend ({_trend_units(cfg)})"


def _map_figure(
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    values: np.ndarray,
    colorbar_label: str,
    coordinate_system: str,
    clim_var_name: str,
    map_type: str,
    switzerland: gpd.GeoDataFrame,
    path: Path,
) -> None:
    x_range = np.nanmax(grid_x) - np.nanmin(grid_x)
    y_range = np.nanmax(grid_y) - np.nanmin(grid_y)
    lon_scale = 1.0
    if coordinate_system == "geographic":
        mean_lat = 0.5 * (np.nanmin(grid_y) + np.nanmax(grid_y))
        lon_scale = np.cos(np.deg2rad(mean_lat))
    plot_height_cm = PLOT_WIDTH_CM * y_range / (x_range * lon_scale)

    fig_width_cm = MARGIN_CM + PLOT_WIDTH_CM + COLORBAR_GAP_CM + COLORBAR_WIDTH_CM + MARGIN_CM
    fig_height_cm = MARGIN_CM + plot_height_cm + MARGIN_CM
    fig = plt.figure(figsize=(fig_width_cm * CM_TO_IN, fig_height_cm * CM_TO_IN))

    ax_left = MARGIN_CM / fig_width_cm
    ax_bottom = MARGIN_CM / fig_height_cm
    ax_width = PLOT_WIDTH_CM / fig_width_cm
    ax_height = plot_height_cm / fig_height_cm
    ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])

    masked_values = _mask_outside_switzerland(grid_x, grid_y, values, switzerland)
    cmap = _map_cmap(clim_var_name, map_type).copy()
    cmap.set_bad("white")
    norm = _map_norm(masked_values, clim_var_name, map_type)
    levels = _map_levels(masked_values, norm)
    contour = ax.contourf(
        grid_x,
        grid_y,
        np.ma.masked_invalid(masked_values),
        levels=levels,
        cmap=cmap,
        norm=norm,
        extend="both",
    )
    switzerland.boundary.plot(ax=ax, color="black", linewidth=BOX_LINE_WIDTH)
    ax.scatter(
        station_x,
        station_y,
        color="black",
        marker="o",
        linewidths=0,
        s=STATION_MARKER_SIZE,
        zorder=3,
    )
    ax.set_xlim(np.nanmin(grid_x), np.nanmax(grid_x))
    ax.set_ylim(np.nanmin(grid_y), np.nanmax(grid_y))
    ax.set_aspect(1 / lon_scale, adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar_left = ax_left + ax_width + COLORBAR_GAP_CM / fig_width_cm
    cbar_height = 0.5 * ax_height
    cbar_bottom = ax_bottom + 0.25 * ax_height
    cbar_width = COLORBAR_WIDTH_CM / fig_width_cm
    cax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])
    cbar = fig.colorbar(contour, cax=cax, orientation="vertical")
    cbar.ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=MAX_COLORBAR_TICKS, min_n_ticks=MIN_TICKS))
    cbar.set_label(colorbar_label, fontsize=FONT_SIZE)
    cbar.ax.tick_params(labelsize=FONT_SIZE, length=TICK_LENGTH_POINTS, width=BOX_LINE_WIDTH)
    cbar.outline.set_linewidth(BOX_LINE_WIDTH)

    fig.savefig(path, dpi=300)
    plt.close(fig)


def _mask_outside_switzerland(
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    values: np.ndarray,
    switzerland: gpd.GeoDataFrame,
) -> np.ndarray:
    geometry = switzerland.geometry.union_all()
    inside = shapely.contains_xy(geometry, grid_x, grid_y)
    return np.where(inside, values, np.nan)


def _map_cmap(clim_var_name: str, map_type: str) -> mcolors.Colormap:
    if _is_centered_map(clim_var_name, map_type):
        return plt.get_cmap(CENTERED_CMAP)
    if clim_var_name == "pr":
        return plt.get_cmap(PRECIPITATION_CMAP)
    return plt.get_cmap(TEMPERATURE_CMAP)


def _map_norm(values: np.ndarray, clim_var_name: str, map_type: str) -> mcolors.Normalize:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return mcolors.Normalize(vmin=0, vmax=1)

    if _is_centered_map(clim_var_name, map_type):
        vmax = float(np.nanmax(np.abs(finite)))
        if vmax == 0:
            vmax = 1
        return mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

    vmin = float(np.nanmin(finite))
    vmax = float(np.nanmax(finite))
    if vmin == vmax:
        vmax = vmin + 1
    return mcolors.Normalize(vmin=vmin, vmax=vmax)


def _map_levels(values: np.ndarray, norm: mcolors.Normalize) -> np.ndarray:
    return np.linspace(float(norm.vmin), float(norm.vmax), 101)


def _is_centered_map(clim_var_name: str, map_type: str) -> bool:
    return clim_var_name == "tas" or map_type == "trend"


if __name__ == "__main__":
    main()
