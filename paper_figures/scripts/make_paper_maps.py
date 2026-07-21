from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from eqm_step import makediagnostics
from eqm_step.config import BiasCorrectionConfig
from eqm_step.diagnostics import Diagnostics
from eqm_step.plotting import (
    BOX_LINE_WIDTH,
    CM_TO_IN,
    FONT_SIZE,
    MIN_TICKS,
    TICK_LENGTH_POINTS,
    _format_units,
    _set_plot_style,
)
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


MAX_COLORBAR_TICKS = 4


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper_figures" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    map_specs = [
        (config_andermatt_zuerich_tas_trends_on(), "mean"),
        (config_andermatt_zuerich_pr_trends_on(), "mean"),
        (config_andermatt_zuerich_tas_trends_on(), "trend"),
        (config_andermatt_zuerich_pr_trends_on(), "trend"),
    ]

    diagnostics_cache: dict[str, Diagnostics] = {}
    for cfg, map_type in map_specs:
        diagnostics = diagnostics_cache.setdefault(cfg.clim_var_name, makediagnostics(cfg))
        _paper_map(diagnostics, cfg, map_type, figure_dir)


def _paper_map(
    diagnostics: Diagnostics,
    cfg: BiasCorrectionConfig,
    map_type: str,
    figure_dir: Path,
) -> None:
    if map_type == "mean":
        values = np.nanmean(diagnostics.bc_grid_clim_var_yearly, axis=2)
        colorbar_label = _mean_label(cfg)
        file_name = f"{cfg.clim_var_name}_paper_long_term_average_map.png"
    elif map_type == "trend":
        values = diagnostics.bc_grid_linear_trends
        colorbar_label = _trend_label(cfg)
        file_name = f"{cfg.clim_var_name}_paper_linear_trend_map.png"
    else:
        raise ValueError("map_type must be 'mean' or 'trend'.")

    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        values,
        colorbar_label,
        figure_dir / file_name,
    )


def _mean_label(cfg: BiasCorrectionConfig) -> str:
    units = _format_units(cfg.clim_var_units)
    if cfg.agg_method == "sum":
        return f"{cfg.clim_var_long_name} ({units} year$^{{-1}}$)"
    return f"{cfg.clim_var_long_name} ({units})"


def _trend_label(cfg: BiasCorrectionConfig) -> str:
    units = _format_units(cfg.clim_var_units)
    if cfg.agg_method == "sum":
        return f"{cfg.clim_var_long_name} trend ({units} year$^{{-2}}$)"
    return f"{cfg.clim_var_long_name} trend ({units} year$^{{-1}}$)"


def _map_figure(
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    values: np.ndarray,
    colorbar_label: str,
    path: Path,
) -> None:
    ll_ratio = (np.nanmax(grid_x) - np.nanmin(grid_x)) / (np.nanmax(grid_y) - np.nanmin(grid_y))
    plot_width_cm = 3
    plot_height_cm = plot_width_cm / ll_ratio
    margin_cm = 2
    colorbar_height_cm = 0.25
    colorbar_gap_cm = 0.35

    fig_width_cm = margin_cm + plot_width_cm + margin_cm
    fig_height_cm = margin_cm + colorbar_height_cm + colorbar_gap_cm + plot_height_cm + margin_cm
    fig = plt.figure(figsize=(fig_width_cm * CM_TO_IN, fig_height_cm * CM_TO_IN))

    ax_left = margin_cm / fig_width_cm
    ax_bottom = (margin_cm + colorbar_height_cm + colorbar_gap_cm) / fig_height_cm
    ax_width = plot_width_cm / fig_width_cm
    ax_height = plot_height_cm / fig_height_cm
    ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])

    contour = ax.contourf(grid_x, grid_y, values, levels=100)
    ax.scatter(
        station_x,
        station_y,
        facecolors="white",
        edgecolors="black",
        marker="o",
        linewidths=BOX_LINE_WIDTH,
        s=24,
    )
    ax.set_xlim(np.nanmin(grid_x), np.nanmax(grid_x))
    ax.set_ylim(np.nanmin(grid_y), np.nanmax(grid_y))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_linewidth(BOX_LINE_WIDTH)

    cbar_left = ax_left
    cbar_bottom = margin_cm / fig_height_cm
    cbar_width = ax_width
    cbar_height = colorbar_height_cm / fig_height_cm
    cax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])
    cbar = fig.colorbar(contour, cax=cax, orientation="horizontal")
    cbar.ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=MAX_COLORBAR_TICKS, min_n_ticks=MIN_TICKS))
    cbar.set_label(colorbar_label, fontsize=FONT_SIZE)
    cbar.ax.tick_params(labelsize=FONT_SIZE, length=TICK_LENGTH_POINTS, width=BOX_LINE_WIDTH)
    cbar.outline.set_linewidth(BOX_LINE_WIDTH)

    fig.savefig(path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
