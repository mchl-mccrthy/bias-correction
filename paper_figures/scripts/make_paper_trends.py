from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from eqtm import makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from eqtm.plotting import _add_equality_line, _new_figure, _save_figure, _set_plot_style, _trend_units
from paper_figures.scripts.make_paper_qq import OFF_COLOR, ON_COLOR, RAW_COLOR
from scripts.config_andermatt_zuerich_pr_trends_off import config_andermatt_zuerich_pr_trends_off
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_off import config_andermatt_zuerich_tas_trends_off
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper_figures" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    _paper_trends(
        config_andermatt_zuerich_tas_trends_on(),
        config_andermatt_zuerich_tas_trends_off(),
        figure_dir,
    )
    _paper_trends(
        config_andermatt_zuerich_pr_trends_on(),
        config_andermatt_zuerich_pr_trends_off(),
        figure_dir,
    )


def _paper_trends(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
    figure_dir: Path,
) -> None:
    diagnostics_on = makediagnostics(cfg_on)
    diagnostics_off = makediagnostics(cfg_off)

    fig, ax = _new_figure(4, 4, 4)
    units = _trend_units(cfg_on)

    raw = ax.scatter(
        diagnostics_on.station_linear_trends,
        diagnostics_on.raw_station_linear_trends,
        color=RAW_COLOR,
        label="Raw",
    )
    bc_on = ax.scatter(
        diagnostics_on.station_linear_trends,
        diagnostics_on.bc_station_linear_trends,
        color=ON_COLOR,
        label="Bias-corrected, station trend mapping",
    )
    bc_off = ax.scatter(
        diagnostics_on.station_linear_trends,
        diagnostics_off.bc_station_linear_trends,
        color=OFF_COLOR,
        label="Bias-corrected, no trend mapping",
    )

    values = np.concatenate(
        [
            diagnostics_on.station_linear_trends,
            diagnostics_on.raw_station_linear_trends,
            diagnostics_on.bc_station_linear_trends,
            diagnostics_off.bc_station_linear_trends,
            np.array([0.0]),
        ]
    )
    values = values[np.isfinite(values)]
    if values.size:
        lims = [np.min(values), np.max(values)]
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        _add_equality_line(ax, lims)

    ax.set_xlabel(f"{cfg_on.clim_var_long_name} trend, stations ({units})")
    ax.set_ylabel(f"{cfg_on.clim_var_long_name} trend, gridded ({units})")
    ax.legend(
        [raw, bc_on, bc_off],
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

    _save_figure(fig, figure_dir / f"{cfg_on.clim_var_name}_paper_linear_trends_scatter.png")


if __name__ == "__main__":
    main()
