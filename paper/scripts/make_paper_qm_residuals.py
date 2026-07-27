from __future__ import annotations

from pathlib import Path

import numpy as np

from eqtm import makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.plotting import _format_units, _new_figure, _save_figure, _set_plot_style
from paper.scripts.make_paper_qq import OFF_COLOR, ON_COLOR, RAW_COLOR, _station_quantiles
from scripts.config_andermatt_zuerich_pr_trends_off import config_andermatt_zuerich_pr_trends_off
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_off import config_andermatt_zuerich_tas_trends_off
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    _paper_qm_residuals(
        config_andermatt_zuerich_tas_trends_on(),
        config_andermatt_zuerich_tas_trends_off(),
        figure_dir,
    )
    _paper_qm_residuals(
        config_andermatt_zuerich_pr_trends_on(),
        config_andermatt_zuerich_pr_trends_off(),
        figure_dir,
    )


def _paper_qm_residuals(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
    figure_dir: Path,
) -> None:
    diagnostics_on = makediagnostics(cfg_on)
    diagnostics_off = makediagnostics(cfg_off)

    fig, ax = _new_figure(4, 2, 4)
    units = _format_units(cfg_on.clim_var_units)
    qs = np.linspace(0, 1, 1000)
    x_min = np.inf
    x_max = -np.inf
    residual_max = 0.0
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

        raw_residual = raw_q - station_q
        on_residual = bc_on_q - station_q
        off_residual = bc_off_q - station_q

        raw_line = ax.plot(station_q, raw_residual, color=RAW_COLOR, linewidth=1, zorder=2)[0]
        on_line = ax.plot(station_q, on_residual, color=ON_COLOR, linewidth=1, zorder=2)[0]
        off_line = ax.plot(station_q, off_residual, color=OFF_COLOR, linewidth=1, zorder=2)[0]
        raw_handle = raw_handle or raw_line
        on_handle = on_handle or on_line
        off_handle = off_handle or off_line

        x_min = min(x_min, np.nanmin(station_q))
        x_max = max(x_max, np.nanmax(station_q))
        residual_max = max(
            residual_max,
            np.nanmax(np.abs(raw_residual)),
            np.nanmax(np.abs(on_residual)),
            np.nanmax(np.abs(off_residual)),
        )

    if np.isfinite(x_min) and np.isfinite(x_max) and x_min < x_max:
        x_pad = 0.05 * (x_max - x_min)
        ax.set_xlim(x_min - x_pad, x_max + x_pad)
    if np.isfinite(residual_max) and residual_max > 0:
        ax.set_ylim(-1.05 * residual_max, 1.05 * residual_max)
    ax.axhline(0, color="k", linestyle=":", linewidth=1, zorder=0)

    ax.set_xlabel(f"{cfg_on.clim_var_long_name}, station ({units})")
    ax.set_ylabel(f"{cfg_on.clim_var_long_name} residual ({units})")
    if raw_handle is not None and on_handle is not None and off_handle is not None:
        ax.legend(
            [raw_handle, on_handle, off_handle],
            [
                "Raw",
                "Bias-corrected, trend mapping on",
                "Bias-corrected, trend mapping off",
            ],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.35),
            borderaxespad=0,
            ncol=1,
        )

    _save_figure(fig, figure_dir / f"{cfg_on.clim_var_name}_qm_residuals.png")


if __name__ == "__main__":
    main()
