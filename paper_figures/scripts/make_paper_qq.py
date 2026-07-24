from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from eqtm import makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from eqtm.plotting import (
    _add_equality_line,
    _format_units,
    _new_figure,
    _padded_equal_lims,
    _save_figure,
    _set_plot_style,
)
from scripts.config_andermatt_zuerich_pr_trends_off import config_andermatt_zuerich_pr_trends_off
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_off import config_andermatt_zuerich_tas_trends_off
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


RAW_COLOR = "0.45"
ON_COLOR = "red"
OFF_COLOR = "blue"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper_figures" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    _paper_qq(
        config_andermatt_zuerich_tas_trends_on(),
        config_andermatt_zuerich_tas_trends_off(),
        figure_dir,
    )
    _paper_qq(
        config_andermatt_zuerich_pr_trends_on(),
        config_andermatt_zuerich_pr_trends_off(),
        figure_dir,
    )


def _paper_qq(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
    figure_dir: Path,
) -> None:
    diagnostics_on = makediagnostics(cfg_on)
    diagnostics_off = makediagnostics(cfg_off)

    fig, ax = _new_figure(4, 4, 4)
    units = _format_units(cfg_on.clim_var_units)
    qs = np.linspace(0, 1, 1000)
    qq_min = np.inf
    qq_max = -np.inf
    raw_handle = None
    on_handle = None
    off_handle = None

    for i_station in range(diagnostics_on.station_clim_var.shape[1]):
        station_q, raw_q, bc_on_q, bc_off_q = _station_quantiles(
            diagnostics_on,
            diagnostics_off,
            i_station,
            qs,
        )
        if station_q is None:
            continue

        raw_line = ax.plot(station_q, raw_q, color=RAW_COLOR, linewidth=1)[0]
        on_line = ax.plot(station_q, bc_on_q, color=ON_COLOR, linewidth=1)[0]
        off_line = ax.plot(station_q, bc_off_q, color=OFF_COLOR, linewidth=1)[0]
        raw_handle = raw_handle or raw_line
        on_handle = on_handle or on_line
        off_handle = off_handle or off_line
        qq_min = min(
            qq_min,
            np.nanmin(station_q),
            np.nanmin(raw_q),
            np.nanmin(bc_on_q),
            np.nanmin(bc_off_q),
        )
        qq_max = max(
            qq_max,
            np.nanmax(station_q),
            np.nanmax(raw_q),
            np.nanmax(bc_on_q),
            np.nanmax(bc_off_q),
        )

    if np.isfinite(qq_min) and np.isfinite(qq_max) and qq_min < qq_max:
        lims = _padded_equal_lims(qq_min, qq_max)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        _add_equality_line(ax, lims)

    ax.set_xlabel(f"{cfg_on.clim_var_long_name}, station ({units})")
    ax.set_ylabel(f"{cfg_on.clim_var_long_name}, gridded ({units})")
    if raw_handle is not None and on_handle is not None and off_handle is not None:
        ax.legend(
            [raw_handle, on_handle, off_handle],
            [
                "Raw",
                "Bias-corrected, station trend mapping",
                "Bias-corrected, no trend mapping",
            ],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.20),
            borderaxespad=0,
            ncol=1,
        )

    _save_figure(fig, figure_dir / f"{cfg_on.clim_var_name}_paper_all_stations_qq.png")


def _station_quantiles(
    diagnostics_on: Diagnostics,
    diagnostics_off: Diagnostics,
    i_station: int,
    qs: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | tuple[None, None, None, None]:
    if not diagnostics_on.station_time.equals(diagnostics_off.station_time):
        raise ValueError("Trend-method diagnostics must use the same station time vector.")
    if not diagnostics_on.grid_time.equals(diagnostics_off.grid_time):
        raise ValueError("Trend-method diagnostics must use the same grid time vector.")
    if not diagnostics_on.station_time.equals(diagnostics_on.grid_time):
        raise ValueError("Station and grid time vectors must match exactly.")

    station = diagnostics_on.station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    raw = diagnostics_on.raw_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    bc_on = diagnostics_on.bc_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    bc_off = diagnostics_off.bc_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    valid = ~np.isnan(station) & ~np.isnan(raw) & ~np.isnan(bc_on) & ~np.isnan(bc_off)

    if not np.any(valid):
        return None, None, None, None

    station_q = np.nanquantile(station[valid], qs, method="hazen")
    raw_q = np.nanquantile(raw[valid], qs, method="hazen")
    bc_on_q = np.nanquantile(bc_on[valid], qs, method="hazen")
    bc_off_q = np.nanquantile(bc_off[valid], qs, method="hazen")
    return station_q, raw_q, bc_on_q, bc_off_q


if __name__ == "__main__":
    main()
