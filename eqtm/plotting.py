from __future__ import annotations

import re
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import BiasCorrectionConfig
from .diagnostics import Diagnostics, getoverlappingstationdata
from .spatial import spatialmean


CM_TO_IN = 1 / 2.54
FONT_SIZE = 7
LINE_WIDTH = 1
BOX_LINE_WIDTH = 0.5
TICK_LENGTH_POINTS = 0.1 * 72 / 2.54
MIN_TICKS = 3
MAX_TICKS = 5
MARKER_SIZE = 10
RAW_COLOR = "0.45"
BC_COLOR = "red"
STATION_COLOR = "black"


def makeplots(diagnostics: Diagnostics, cfg: BiasCorrectionConfig) -> None:
    """Create diagnostic figures for an EQTM workflow run.

    Figures include maps of long-term mean and Theil-Sen slope fields, station slope
    comparisons, all-station quantile-quantile and residual plots, station
    availability, and per-station diagnostic plots.
    """

    figure_dir = Path(cfg.file_path_figures_tables)
    overview_dir = figure_dir / "overview"
    individual_stations_dir = figure_dir / "individual_stations"
    overview_dir.mkdir(parents=True, exist_ok=True)
    individual_stations_dir.mkdir(parents=True, exist_ok=True)
    _set_plot_style()
    plotmaps(diagnostics, cfg, overview_dir)
    plotoverviewtimesteptimeseries(diagnostics, cfg, overview_dir)
    plotoverviewtimeseries(diagnostics, cfg, overview_dir)
    plottrendcomparison(diagnostics, cfg, overview_dir)
    plotquantilemae(diagnostics, cfg, overview_dir)
    plotannualmae(diagnostics, cfg, overview_dir)
    plottrendmae(diagnostics, cfg, overview_dir)
    plotallstationsqq(diagnostics, cfg, overview_dir)
    plotallstationsqmresiduals(diagnostics, cfg, overview_dir)
    plotstationavailability(diagnostics, cfg, overview_dir)
    plotstationdiagnostics(diagnostics, cfg, individual_stations_dir)


def plotmaps(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    mean_grid = np.nanmean(diagnostics.bc_grid_clim_var_yearly, axis=2)
    units = _yearly_units(cfg)
    slope_units = _trend_units(cfg)
    mean_label = f"{cfg.clim_var_long_name} ({units})"
    slope_label = f"{cfg.clim_var_long_name} trend ({slope_units})"

    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        mean_grid,
        "Domain temporal average",
        mean_label,
        cfg.coordinate_system,
        figure_dir / f"{cfg.clim_var_name}_long_term_average_map.png",
    )
    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        diagnostics.bc_grid_theil_sen_slopes,
        "Domain trend",
        slope_label,
        cfg.coordinate_system,
        figure_dir / f"{cfg.clim_var_name}_bc_trend_map.png",
    )


def plottrendcomparison(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    _trendcomparisonfigure(
        diagnostics.station_theil_sen_slopes,
        diagnostics.raw_station_theil_sen_slopes,
        diagnostics.bc_station_theil_sen_slopes,
        cfg,
        "trend",
        figure_dir / f"{cfg.clim_var_name}_trends_scatter.png",
    )


def plotoverviewtimeseries(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(7, 2, 4)
    units = _yearly_units(cfg)
    raw_domain_mean = spatialmean(
        diagnostics.raw_grid_clim_var_yearly, diagnostics.grid_y, cfg.coordinate_system
    )
    bc_domain_mean = spatialmean(
        diagnostics.bc_grid_clim_var_yearly, diagnostics.grid_y, cfg.coordinate_system
    )
    ax.plot(diagnostics.years, raw_domain_mean, color=RAW_COLOR, label="Raw")
    ax.plot(diagnostics.years, bc_domain_mean, color=BC_COLOR, label="Bias-corrected")
    ax.set_ylabel(f"{cfg.clim_var_long_name} ({units})")
    ax.set_xlim(np.min(diagnostics.years), np.max(diagnostics.years))
    ax.set_title("Domain spatial average, yearly")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_domain_mean_time_series_yearly.png")


def plotoverviewtimesteptimeseries(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(7, 2, 4)
    units = _format_units(cfg.clim_var_units)
    ax.plot(diagnostics.grid_time, diagnostics.raw_grid_domain_mean, color=RAW_COLOR, label="Raw")
    ax.plot(diagnostics.grid_time, diagnostics.bc_grid_domain_mean, color=BC_COLOR, label="Bias-corrected")
    ax.set_ylabel(f"{cfg.clim_var_long_name} ({units})")
    ax.set_xlim(diagnostics.grid_time[0], diagnostics.grid_time[-1])
    ax.set_title("Domain spatial average, time step")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _format_date_axis(ax)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_domain_mean_time_series.png")


def plotannualmae(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(4, 2, 4)
    handles = _stripplot(
        ax,
        [
            diagnostics.raw_station_annual_mae,
            diagnostics.bc_station_annual_mae,
        ],
        ["Raw", "Bias-corrected"],
        [RAW_COLOR, BC_COLOR],
    )
    ax.set_xlabel(f"MAE, yearly {cfg.clim_var_long_name.lower()} ({_yearly_units(cfg)})")
    ax.set_title("All stations, yearly MAE")
    ax.legend(handles, ["Raw", "Bias-corrected"], loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_annual_mae_strip.png")


def plotquantilemae(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(4, 2, 4)
    handles = _stripplot(
        ax,
        [
            diagnostics.raw_station_quantile_mae,
            diagnostics.bc_station_quantile_mae,
        ],
        ["Raw", "Bias-corrected"],
        [RAW_COLOR, BC_COLOR],
    )
    ax.set_xlabel(f"MAE, {cfg.clim_var_long_name.lower()} quantiles ({_format_units(cfg.clim_var_units)})")
    ax.set_title("All stations, quantile MAE")
    ax.legend(handles, ["Raw", "Bias-corrected"], loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_quantile_mae_strip.png")


def plottrendmae(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(4, 2, 4)
    raw_trend_ae = np.abs(diagnostics.raw_station_theil_sen_slopes - diagnostics.station_theil_sen_slopes)
    bc_trend_ae = np.abs(diagnostics.bc_station_theil_sen_slopes - diagnostics.station_theil_sen_slopes)
    handles = _stripplot(
        ax,
        [
            raw_trend_ae,
            bc_trend_ae,
        ],
        ["Raw", "Bias-corrected"],
        [RAW_COLOR, BC_COLOR],
    )
    ax.set_xlabel(f"AE, {cfg.clim_var_long_name.lower()} trend ({_trend_units(cfg)})")
    ax.set_title("All stations, trend absolute error")
    ax.legend(handles, ["Raw", "Bias-corrected"], loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_trend_mae_strip.png")


def _trendcomparisonfigure(
    station_trends: np.ndarray,
    raw_station_trends: np.ndarray,
    bc_station_trends: np.ndarray,
    cfg: BiasCorrectionConfig,
    trend_label: str,
    path: Path,
) -> None:
    fig, ax = _new_figure(4, 4, 4)
    units = _trend_units(cfg)
    ax.scatter(
        station_trends,
        raw_station_trends,
        color=RAW_COLOR,
        s=MARKER_SIZE,
        label="Raw",
    )
    ax.scatter(
        station_trends,
        bc_station_trends,
        color=BC_COLOR,
        s=MARKER_SIZE,
        label="Bias-corrected",
    )
    ax.set_xlabel(f"{cfg.clim_var_long_name} {trend_label}, stations ({units})")
    ax.set_ylabel(f"{cfg.clim_var_long_name} {trend_label}, gridded ({units})")
    ax.set_title("All stations, trends")

    values = np.concatenate(
        [
            station_trends,
            raw_station_trends,
            bc_station_trends,
            np.array([0.0]),
        ]
    )
    values = values[np.isfinite(values)]
    if values.size:
        lims = _padded_equal_lims(np.min(values), np.max(values))
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        _add_equality_line(ax, lims)

    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, path)


def plotallstationsqq(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(4, 4, 4)
    units = _format_units(cfg.clim_var_units)
    qs = np.linspace(0, 1, 1000)
    qq_min = np.inf
    qq_max = -np.inf
    raw_handle = None
    bc_handle = None

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

        station_q = np.nanquantile(station_overlap, qs, method="hazen")
        raw_q = np.nanquantile(raw_overlap, qs, method="hazen")
        bc_q = np.nanquantile(bc_overlap, qs, method="hazen")
        raw_line = ax.plot(station_q, raw_q, color=RAW_COLOR, linewidth=1)[0]
        bc_line = ax.plot(station_q, bc_q, color=BC_COLOR, linewidth=1)[0]
        raw_handle = raw_handle or raw_line
        bc_handle = bc_handle or bc_line
        qq_min = min(qq_min, np.nanmin(station_q), np.nanmin(raw_q), np.nanmin(bc_q))
        qq_max = max(qq_max, np.nanmax(station_q), np.nanmax(raw_q), np.nanmax(bc_q))

    if np.isfinite(qq_min) and np.isfinite(qq_max) and qq_min < qq_max:
        lims = _padded_equal_lims(qq_min, qq_max)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        _add_equality_line(ax, lims)
    ax.set_xlabel(f"{cfg.clim_var_long_name}, station ({units})")
    ax.set_ylabel(f"{cfg.clim_var_long_name}, gridded ({units})")
    ax.set_title("All stations, quantile-quantile")
    if raw_handle is not None and bc_handle is not None:
        ax.legend(
            [raw_handle, bc_handle],
            ["Raw", "Bias-corrected"],
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0,
        )
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_all_stations_qq.png")


def plotallstationsqmresiduals(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(4, 2, 4)
    units = _format_units(cfg.clim_var_units)
    qs = np.linspace(0, 1, 1000)
    x_min = np.inf
    x_max = -np.inf
    residual_max = 0.0
    raw_handle = None
    bc_handle = None

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

        station_q = np.nanquantile(station_overlap, qs, method="hazen")
        raw_q = np.nanquantile(raw_overlap, qs, method="hazen")
        bc_q = np.nanquantile(bc_overlap, qs, method="hazen")
        raw_residual = raw_q - station_q
        bc_residual = bc_q - station_q

        raw_line = ax.plot(station_q, raw_residual, color=RAW_COLOR, linewidth=1, zorder=2)[0]
        bc_line = ax.plot(station_q, bc_residual, color=BC_COLOR, linewidth=1, zorder=2)[0]
        raw_handle = raw_handle or raw_line
        bc_handle = bc_handle or bc_line

        x_min = min(x_min, np.nanmin(station_q))
        x_max = max(x_max, np.nanmax(station_q))
        residual_max = max(
            residual_max,
            np.nanmax(np.abs(raw_residual)),
            np.nanmax(np.abs(bc_residual)),
        )

    if np.isfinite(x_min) and np.isfinite(x_max) and x_min < x_max:
        x_pad = 0.05 * (x_max - x_min)
        ax.set_xlim(x_min - x_pad, x_max + x_pad)
    if np.isfinite(residual_max) and residual_max > 0:
        ax.set_ylim(-1.05 * residual_max, 1.05 * residual_max)
    ax.axhline(0, color="k", linestyle=":", linewidth=LINE_WIDTH, zorder=0)

    ax.set_xlabel(f"{cfg.clim_var_long_name}, station ({units})")
    ax.set_ylabel(f"{cfg.clim_var_long_name} residual ({units})")
    ax.set_title("All stations, quantile residuals")
    if raw_handle is not None and bc_handle is not None:
        ax.legend(
            [raw_handle, bc_handle],
            ["Raw", "Bias-corrected"],
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0,
        )
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_all_stations_qm_residuals.png")


def plotstationavailability(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    station_names = _station_names(diagnostics)
    n_stations = diagnostics.station_clim_var.shape[1]
    fig, ax = _new_figure(5, 0.5 * n_stations, 4)

    for i_station, column in enumerate(diagnostics.station_clim_var.columns):
        valid = ~diagnostics.station_clim_var[column].isna()
        ax.scatter(
            diagnostics.station_time[valid],
            np.full(valid.sum(), i_station + 1),
            color="blue",
            s=MARKER_SIZE,
        )
        ax.text(
            diagnostics.station_time[-1] + pd.DateOffset(years=1),
            i_station + 1,
            station_names[i_station],
            fontsize=FONT_SIZE,
        )

    ax.set_xlim(diagnostics.station_time[0], diagnostics.station_time[-1])
    ax.set_ylim(0, n_stations + 1)
    ax.set_yticklabels([])
    ax.set_title("Station availability")
    _format_date_axis(ax)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_station_availability.png")


def plotstationdiagnostics(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    station_names = _station_names(diagnostics)
    for i_station, station_name in enumerate(station_names):
        _plot_station_timestep_timeseries(diagnostics, cfg, figure_dir, i_station, station_name)

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

        hist_min = np.nanmin(np.concatenate([raw_overlap, bc_overlap, station_overlap]))
        hist_max = np.nanmax(np.concatenate([raw_overlap, bc_overlap, station_overlap]))
        if not np.isfinite(hist_min) or not np.isfinite(hist_max) or hist_min == hist_max:
            continue

        _plot_station_histogram(
            cfg, figure_dir, station_name, raw_overlap, bc_overlap, station_overlap, hist_min, hist_max
        )
        _plot_station_qq(
            cfg, figure_dir, station_name, raw_overlap, bc_overlap, station_overlap, hist_min, hist_max
        )
        _plot_station_yearly_timeseries(diagnostics, cfg, figure_dir, i_station, station_name)


def _plot_station_timestep_timeseries(
    diagnostics: Diagnostics,
    cfg: BiasCorrectionConfig,
    figure_dir: Path,
    i_station: int,
    station_name: str,
) -> None:
    fig, ax = _new_figure(7, 2, 4)
    units = _format_units(cfg.clim_var_units)
    ax.plot(diagnostics.grid_time, diagnostics.raw_station_clim_var.iloc[:, i_station], color=RAW_COLOR, label="Raw")
    ax.plot(
        diagnostics.grid_time,
        diagnostics.bc_station_clim_var.iloc[:, i_station],
        color=BC_COLOR,
        label="Bias-corrected",
    )
    ax.plot(
        diagnostics.station_time,
        diagnostics.station_clim_var.iloc[:, i_station],
        color=STATION_COLOR,
        label="Station",
    )
    ax.set_ylabel(f"{cfg.clim_var_long_name} ({units})")
    ax.set_xlim(diagnostics.grid_time[0], diagnostics.grid_time[-1])
    ax.set_title(station_name)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _format_date_axis(ax)
    _save_figure(fig, figure_dir / f"{station_name}_{cfg.clim_var_name}_time_series.png")


def _plot_station_histogram(
    cfg: BiasCorrectionConfig,
    figure_dir: Path,
    station_name: str,
    raw_overlap: np.ndarray,
    bc_overlap: np.ndarray,
    station_overlap: np.ndarray,
    hist_min: float,
    hist_max: float,
) -> None:
    fig, ax = _new_figure(4, 4, 4)
    units = _format_units(cfg.clim_var_units)
    edges = np.linspace(hist_min, hist_max, 25)
    ax.hist(raw_overlap, edges, label="Raw", alpha=0.4)
    ax.hist(bc_overlap, edges, label="Bias-corrected", alpha=0.4)
    ax.hist(station_overlap, edges, label="Station", alpha=0.4)
    ax.set_ylabel("Count")
    ax.set_xlabel(f"{cfg.clim_var_long_name} ({units})")
    ax.set_title(station_name)
    ax.set_xlim(hist_min, hist_max)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{station_name}_{cfg.clim_var_name}_histogram.png")


def _plot_station_qq(
    cfg: BiasCorrectionConfig,
    figure_dir: Path,
    station_name: str,
    raw_overlap: np.ndarray,
    bc_overlap: np.ndarray,
    station_overlap: np.ndarray,
    hist_min: float,
    hist_max: float,
) -> None:
    fig, ax = _new_figure(4, 4, 4)
    units = _format_units(cfg.clim_var_units)
    q = np.linspace(0, 1, 1000)
    station_q = np.nanquantile(station_overlap, q, method="hazen")
    raw_q = np.nanquantile(raw_overlap, q, method="hazen")
    bc_q = np.nanquantile(bc_overlap, q, method="hazen")
    ax.plot(station_q, raw_q, color=RAW_COLOR, label="Raw")
    ax.plot(station_q, bc_q, color=BC_COLOR, label="Bias-corrected")
    ax.set_ylabel(f"{cfg.clim_var_long_name}, gridded ({units})")
    ax.set_xlabel(f"{cfg.clim_var_long_name}, station ({units})")
    ax.set_title(station_name)
    lims = _padded_equal_lims(hist_min, hist_max)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    _add_equality_line(ax, lims)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{station_name}_{cfg.clim_var_name}_qq.png")


def _plot_station_yearly_timeseries(
    diagnostics: Diagnostics,
    cfg: BiasCorrectionConfig,
    figure_dir: Path,
    i_station: int,
    station_name: str,
) -> None:
    fig, ax = _new_figure(7, 2, 4)
    units = _yearly_units(cfg)
    ax.plot(
        diagnostics.years,
        diagnostics.raw_station_clim_var_yearly.iloc[:, i_station],
        color=RAW_COLOR,
        label="Raw",
    )
    ax.plot(
        diagnostics.years,
        diagnostics.bc_station_clim_var_yearly.iloc[:, i_station],
        color=BC_COLOR,
        label="Bias-corrected",
    )
    ax.plot(
        diagnostics.years,
        diagnostics.station_clim_var_yearly.iloc[:, i_station],
        color=STATION_COLOR,
        label="Station",
    )
    ax.set_ylabel(f"{cfg.clim_var_long_name} ({units})")
    ax.set_xlim(np.min(diagnostics.years), np.max(diagnostics.years))
    ax.set_title(station_name)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{station_name}_{cfg.clim_var_name}_time_series_yearly.png")


def _map_figure(
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    values: np.ndarray,
    title: str,
    colorbar_label: str,
    coordinate_system: str,
    path: Path,
) -> None:
    x_range = np.nanmax(grid_x) - np.nanmin(grid_x)
    y_range = np.nanmax(grid_y) - np.nanmin(grid_y)
    lon_scale = 1.0
    if coordinate_system == "geographic":
        mean_lat = 0.5 * (np.nanmin(grid_y) + np.nanmax(grid_y))
        lon_scale = np.cos(np.deg2rad(mean_lat))
    map_area_cm2 = 25
    map_ratio = x_range * lon_scale / y_range
    plot_width_cm = np.sqrt(map_area_cm2 * map_ratio)
    plot_height_cm = np.sqrt(map_area_cm2 / map_ratio)
    fig, ax = _new_figure(plot_width_cm, plot_height_cm, 2)
    contour = ax.contourf(grid_x, grid_y, values, levels=100)
    ax.set_xlim(np.nanmin(grid_x), np.nanmax(grid_x))
    ax.set_ylim(np.nanmin(grid_y), np.nanmax(grid_y))
    ax.set_aspect(1 / lon_scale, adjustable="box")
    cbar = fig.colorbar(contour, cax=_colorbar_axes(fig, ax))
    cbar.ax._eqtm_colorbar = True
    cbar.set_label(colorbar_label)
    cbar.ax.tick_params(labelsize=FONT_SIZE, length=TICK_LENGTH_POINTS, width=BOX_LINE_WIDTH)
    cbar.ax.yaxis.label.set_size(FONT_SIZE)
    cbar.outline.set_linewidth(BOX_LINE_WIDTH)
    station_handle = ax.scatter(
        station_x,
        station_y,
        facecolors="white",
        edgecolors="black",
        marker="o",
        linewidths=BOX_LINE_WIDTH,
        s=MARKER_SIZE,
        label="Stations",
    )
    ax.set_title(title)
    ax.legend(
        [station_handle],
        ["Stations"],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        frameon=False,
        borderaxespad=0,
    )
    _save_figure(fig, path)


def _station_names(diagnostics: Diagnostics) -> list[str]:
    if "station" in diagnostics.station_coords:
        return [str(value) for value in diagnostics.station_coords["station"]]
    return [str(value) for value in diagnostics.station_clim_var.columns]


def _format_units(units: str) -> str:
    formatted = str(units).strip()
    formatted = formatted.replace("\\circC", "\N{DEGREE SIGN}C")
    formatted = formatted.replace("degC", "\N{DEGREE SIGN}C")
    formatted = re.sub(r"\^(-?\d+)", r"^{\1}", formatted)
    formatted = re.sub(r"(?<!\$)\^\{(-?\d+)\}(?!\$)", r"$^{\1}$", formatted)
    formatted = re.sub(r"\b([A-Za-z]+)-(\d+)\b", r"\1$^{-\2}$", formatted)
    return formatted


def _yearly_units(cfg: BiasCorrectionConfig) -> str:
    if cfg.agg_method == "sum":
        units = _format_units(_remove_terminal_inverse_timestep(cfg.clim_var_units))
        return _append_unit_factor(units, "year$^{-1}$")
    return _format_units(cfg.clim_var_units)


def _trend_units(cfg: BiasCorrectionConfig) -> str:
    if cfg.agg_method == "sum":
        units = _format_units(_remove_terminal_inverse_timestep(cfg.clim_var_units))
        return _append_unit_factor(units, "year$^{-2}$")
    units = _format_units(cfg.clim_var_units)
    return _append_unit_factor(units, "year$^{-1}$")


def _remove_terminal_inverse_timestep(units: str) -> str:
    pattern = (
        r"(?:^|\s+)"
        r"(?:day|days|d|hour|hours|hr|hrs|h)"
        r"(?:-1|\^-?1|\^\{-?1\}|\$\^\{-?1\}\$)"
        r"\s*$"
    )
    return re.sub(pattern, "", str(units).strip(), flags=re.IGNORECASE)


def _append_unit_factor(units: str, factor: str) -> str:
    if units:
        return f"{units} {factor}"
    return factor


def _add_equality_line(ax: plt.Axes, lims: list[float] | tuple[float, float]) -> None:
    ax.plot(lims, lims, color="k", linestyle=":", linewidth=LINE_WIDTH, label="_nolegend_", zorder=0)


def _padded_equal_lims(lim_min: float, lim_max: float) -> list[float]:
    span = lim_max - lim_min
    if not np.isfinite(span) or span <= 0:
        pad = 0.5 if lim_min == 0 else abs(lim_min) * 0.05
    else:
        pad = 0.05 * span
    return [lim_min - pad, lim_max + pad]


def _stripplot(
    ax: plt.Axes,
    values_by_group: list[np.ndarray],
    labels: list[str],
    colors: list[str],
) -> list[plt.Artist]:
    ax._eqtm_categorical_y = True
    handles = []
    for i_group, values in enumerate(values_by_group):
        values = np.asarray(values, dtype=float)
        values = values[np.isfinite(values)]
        y = np.full(values.size, i_group, dtype=float) + _deterministic_jitter(values.size)
        handle = ax.scatter(values, y, color=colors[i_group], s=MARKER_SIZE, zorder=2)
        handles.append(handle)
        if values.size:
            ax.plot(
                [np.nanmedian(values), np.nanmedian(values)],
                [i_group - 0.18, i_group + 0.18],
                color="k",
                linewidth=LINE_WIDTH,
                zorder=3,
            )
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.set_ylim(-0.5, len(labels) - 0.5)
    return handles


def _deterministic_jitter(n_values: int) -> np.ndarray:
    if n_values <= 1:
        return np.zeros(n_values)
    return np.linspace(-0.12, 0.12, n_values)


def _set_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": FONT_SIZE,
            "axes.titlesize": FONT_SIZE,
            "axes.labelsize": FONT_SIZE,
            "xtick.labelsize": FONT_SIZE,
            "ytick.labelsize": FONT_SIZE,
            "legend.fontsize": FONT_SIZE,
            "legend.frameon": False,
            "lines.linewidth": LINE_WIDTH,
            "patch.linewidth": LINE_WIDTH,
            "axes.linewidth": BOX_LINE_WIDTH,
        }
    )


def _new_figure(plot_width_cm: float, plot_height_cm: float, margin_cm: float) -> tuple[plt.Figure, plt.Axes]:
    fig_width = (margin_cm + plot_width_cm + margin_cm) * CM_TO_IN
    fig_height = (margin_cm + plot_height_cm + margin_cm) * CM_TO_IN
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    left = margin_cm / (margin_cm + plot_width_cm + margin_cm)
    bottom = margin_cm / (margin_cm + plot_height_cm + margin_cm)
    width = plot_width_cm / (margin_cm + plot_width_cm + margin_cm)
    height = plot_height_cm / (margin_cm + plot_height_cm + margin_cm)
    ax.set_position([left, bottom, width, height])
    _format_axes(ax)
    return fig, ax


def _format_axes(ax: plt.Axes) -> None:
    ax.title.set_fontsize(FONT_SIZE)
    ax.title.set_fontweight("bold")
    ax.xaxis.label.set_fontsize(FONT_SIZE)
    ax.yaxis.label.set_fontsize(FONT_SIZE)
    ax.tick_params(
        axis="both",
        which="both",
        labelsize=FONT_SIZE,
        length=TICK_LENGTH_POINTS,
        width=BOX_LINE_WIDTH,
        direction="in",
        top=True,
        right=True,
    )
    _format_numeric_ticks(ax)
    if getattr(ax, "_eqtm_colorbar", False):
        ax.xaxis.set_ticks([])
        ax.xaxis.set_ticklabels([])
        ax.xaxis.offsetText.set_visible(False)
    for label in ax.get_xticklabels():
        label.set_rotation(0)
        label.set_horizontalalignment("center")
    for spine in ax.spines.values():
        spine.set_linewidth(BOX_LINE_WIDTH)
    for line in ax.lines:
        line.set_linewidth(LINE_WIDTH)
    for text in ax.texts:
        text.set_fontsize(FONT_SIZE)
    legend = ax.get_legend()
    if legend is not None:
        legend.set_frame_on(False)
        for text in legend.get_texts():
            text.set_fontsize(FONT_SIZE)
        for handle in legend.legend_handles:
            if hasattr(handle, "set_linewidth"):
                handle.set_linewidth(LINE_WIDTH)


def _format_figure(fig: plt.Figure) -> None:
    for ax in fig.axes:
        _format_axes(ax)


def _colorbar_axes(fig: plt.Figure, ax: plt.Axes) -> plt.Axes:
    position = ax.get_position()
    fig_width_cm = fig.get_figwidth() / CM_TO_IN
    gap = 0.25 / fig_width_cm
    width = 0.20 / fig_width_cm
    return fig.add_axes([position.x1 + gap, position.y0, width, position.height])


def _format_date_axis(ax: plt.Axes) -> None:
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=MIN_TICKS, maxticks=MAX_TICKS))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))


def _format_numeric_ticks(ax: plt.Axes) -> None:
    max_ticks = getattr(ax, "_eqtm_max_ticks", MAX_TICKS)
    if not getattr(ax, "_eqtm_colorbar", False) and not _has_date_axis(ax, "x"):
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=max_ticks, min_n_ticks=MIN_TICKS))
    if not getattr(ax, "_eqtm_categorical_y", False) and not _has_date_axis(ax, "y"):
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=max_ticks, min_n_ticks=MIN_TICKS))


def _has_date_axis(ax: plt.Axes, axis_name: str) -> bool:
    axis = ax.xaxis if axis_name == "x" else ax.yaxis
    return isinstance(axis.get_major_locator(), mdates.DateLocator)


def _save_figure(fig: plt.Figure, path: Path) -> None:
    _format_figure(fig)
    fig.savefig(path, dpi=300)
    plt.close(fig)
