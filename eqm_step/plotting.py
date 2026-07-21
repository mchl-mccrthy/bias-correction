from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import BiasCorrectionConfig
from .diagnostics import Diagnostics, getoverlappingstationdata


CM_TO_IN = 1 / 2.54
FONT_SIZE = 7
LINE_WIDTH = 1
BOX_LINE_WIDTH = 0.5
TICK_LENGTH_POINTS = 2
MIN_TICKS = 3
MAX_TICKS = 6
RAW_COLOR = "tab:green"
BC_COLOR = "tab:blue"
STATION_COLOR = "tab:red"


def makeplots(diagnostics: Diagnostics, cfg: BiasCorrectionConfig) -> None:
    """Create diagnostic figures for an EQM-STeP workflow run.

    Figures include maps of long-term mean and trend fields, station trend
    comparisons, all-station quantile-quantile plots, station availability,
    and per-station diagnostic plots.
    """

    figure_dir = Path(cfg.file_path_figures)
    figure_dir.mkdir(parents=True, exist_ok=True)
    _set_plot_style()
    plotmaps(diagnostics, cfg, figure_dir)
    plottrendcomparison(diagnostics, cfg, figure_dir)
    plotallstationsqq(diagnostics, cfg, figure_dir)
    plotstationavailability(diagnostics, cfg, figure_dir)
    plotstationdiagnostics(diagnostics, cfg, figure_dir)


def plotmaps(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    mean_grid = np.nanmean(diagnostics.bc_grid_clim_var_yearly, axis=2)
    units = _format_units(cfg.clim_var_units)
    trend_units = _trend_units(cfg)
    if cfg.agg_method == "sum":
        mean_label = f"{cfg.clim_var_long_name} ({units} year$^{{-1}}$)"
    else:
        mean_label = f"{cfg.clim_var_long_name} ({units})"
    trend_label = f"{cfg.clim_var_long_name} trend ({trend_units})"

    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        mean_grid,
        "Long-term average",
        mean_label,
        figure_dir / f"{cfg.clim_var_name}_long_term_average_map.png",
    )
    _map_figure(
        diagnostics.grid_x,
        diagnostics.grid_y,
        diagnostics.station_x,
        diagnostics.station_y,
        diagnostics.bc_grid_linear_trends,
        "Long-term trend",
        trend_label,
        figure_dir / f"{cfg.clim_var_name}_bc_linear_trend_map.png",
    )


def plottrendcomparison(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(4, 4, 4)
    units = _trend_units(cfg)
    ax.scatter(diagnostics.station_linear_trends, diagnostics.raw_station_linear_trends, label="Raw")
    ax.scatter(diagnostics.station_linear_trends, diagnostics.bc_station_linear_trends, label="Bias-corrected")
    ax.set_xlabel(f"{cfg.clim_var_long_name} trend, stations ({units})")
    ax.set_ylabel(f"{cfg.clim_var_long_name} trend, gridded ({units})")

    values = np.concatenate(
        [
            diagnostics.station_linear_trends,
            diagnostics.raw_station_linear_trends,
            diagnostics.bc_station_linear_trends,
            np.array([0.0]),
        ]
    )
    values = values[np.isfinite(values)]
    if values.size:
        lims = [np.min(values), np.max(values)]
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        _add_equality_line(ax, lims)

    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_linear_trends_scatter.png")


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
        raw_line = ax.plot(station_q, raw_q, color="r", linewidth=1)[0]
        bc_line = ax.plot(station_q, bc_q, color="b", linewidth=1)[0]
        raw_handle = raw_handle or raw_line
        bc_handle = bc_handle or bc_line
        qq_min = min(qq_min, np.nanmin(station_q), np.nanmin(raw_q), np.nanmin(bc_q))
        qq_max = max(qq_max, np.nanmax(station_q), np.nanmax(raw_q), np.nanmax(bc_q))

    if np.isfinite(qq_min) and np.isfinite(qq_max) and qq_min < qq_max:
        ax.set_xlim(qq_min, qq_max)
        ax.set_ylim(qq_min, qq_max)
        _add_equality_line(ax, [qq_min, qq_max])
    ax.set_xlabel(f"{cfg.clim_var_long_name}, station ({units})")
    ax.set_ylabel(f"{cfg.clim_var_long_name}, gridded ({units})")
    ax.set_title("Quantile-quantile")
    if raw_handle is not None and bc_handle is not None:
        ax.legend(
            [raw_handle, bc_handle],
            ["Raw", "Bias-corrected"],
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0,
        )
    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_all_stations_qq.png")


def plotstationavailability(diagnostics: Diagnostics, cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    fig, ax = _new_figure(5, 3, 4)
    station_names = _station_names(diagnostics)
    n_stations = diagnostics.station_clim_var.shape[1]

    for i_station, column in enumerate(diagnostics.station_clim_var.columns):
        valid = ~diagnostics.station_clim_var[column].isna()
        ax.scatter(
            diagnostics.station_time[valid],
            np.full(valid.sum(), i_station + 1),
            color="blue",
            s=6,
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
    ax.plot(station_q, raw_q, color="r", label="Raw")
    ax.plot(station_q, bc_q, color="b", label="Bias-corrected")
    ax.set_ylabel(f"{cfg.clim_var_long_name}, gridded ({units})")
    ax.set_xlabel(f"{cfg.clim_var_long_name}, station ({units})")
    ax.set_title(station_name)
    ax.set_xlim(hist_min, hist_max)
    ax.set_ylim(hist_min, hist_max)
    _add_equality_line(ax, [hist_min, hist_max])
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
    path: Path,
) -> None:
    ll_ratio = (np.nanmax(grid_x) - np.nanmin(grid_x)) / (np.nanmax(grid_y) - np.nanmin(grid_y))
    fig, ax = _new_figure(4, 4 / ll_ratio, 2)
    contour = ax.contourf(grid_x, grid_y, values, levels=100)
    ax.set_xlim(np.nanmin(grid_x), np.nanmax(grid_x))
    ax.set_ylim(np.nanmin(grid_y), np.nanmax(grid_y))
    ax.set_aspect("equal", adjustable="box")
    cbar = fig.colorbar(contour, cax=_colorbar_axes(fig, ax))
    cbar.ax._eqm_step_colorbar = True
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
    return units.replace("degC", "\N{DEGREE SIGN}C")


def _yearly_units(cfg: BiasCorrectionConfig) -> str:
    units = _format_units(cfg.clim_var_units)
    if cfg.agg_method == "sum":
        return f"{units} year$^{{-1}}$"
    return units


def _trend_units(cfg: BiasCorrectionConfig) -> str:
    units = _format_units(cfg.clim_var_units)
    if cfg.agg_method == "sum":
        return f"{units} year$^{{-2}}$"
    return f"{units} year$^{{-1}}$"


def _add_equality_line(ax: plt.Axes, lims: list[float] | tuple[float, float]) -> None:
    ax.plot(lims, lims, color="k", linestyle=":", linewidth=LINE_WIDTH, label="_nolegend_", zorder=0)


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
    )
    _format_numeric_ticks(ax)
    if getattr(ax, "_eqm_step_colorbar", False):
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
    if not getattr(ax, "_eqm_step_colorbar", False) and not _has_date_axis(ax, "x"):
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=MAX_TICKS, min_n_ticks=MIN_TICKS))
    if not _has_date_axis(ax, "y"):
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=MAX_TICKS, min_n_ticks=MIN_TICKS))


def _has_date_axis(ax: plt.Axes, axis_name: str) -> bool:
    axis = ax.xaxis if axis_name == "x" else ax.yaxis
    return isinstance(axis.get_major_locator(), mdates.DateLocator)


def _save_figure(fig: plt.Figure, path: Path) -> None:
    _format_figure(fig)
    fig.savefig(path, dpi=300)
    plt.close(fig)
