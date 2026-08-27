from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from eqtm.plotting import _new_figure, _save_figure, _set_plot_style, _stripplot, _yearly_units
from paper.scripts.diagnostics_cache import makediagnostics_cached as makediagnostics
from paper.scripts.make_paper_qq import OFF_COLOR, ON_COLOR, RAW_COLOR
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures_and_tables"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    _paper_annual_mae(
        config_switzerland_tas_trends_on(),
        config_switzerland_tas_trends_off(),
        figure_dir,
    )
    _paper_annual_mae(
        config_switzerland_pr_trends_on(),
        config_switzerland_pr_trends_off(),
        figure_dir,
    )


def _paper_annual_mae(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
    figure_dir: Path,
) -> None:
    diagnostics_on = makediagnostics(cfg_on)
    diagnostics_off = makediagnostics(cfg_off)
    _check_matching_diagnostics(diagnostics_on, diagnostics_off)

    fig, ax = _new_figure(4, 2, 4)
    _stripplot(
        ax,
        [
            diagnostics_on.raw_station_annual_mae,
            diagnostics_on.bc_station_annual_mae,
            diagnostics_off.bc_station_annual_mae,
        ],
        [
            "Raw",
            "Bias-corrected, trend mapping on",
            "Bias-corrected, trend mapping off",
        ],
        [RAW_COLOR, ON_COLOR, OFF_COLOR],
    )
    ax.set_xlabel(f"MAE, yearly {cfg_on.clim_var_long_name.lower()} ({_yearly_units(cfg_on)})")
    _save_figure(fig, figure_dir / f"{cfg_on.clim_var_name}_annual_mae_strip.png")


def _check_matching_diagnostics(diagnostics_on: Diagnostics, diagnostics_off: Diagnostics) -> None:
    if not diagnostics_on.station_time.equals(diagnostics_off.station_time):
        raise ValueError("Trend-method diagnostics must use the same station time vector.")
    if not diagnostics_on.grid_time.equals(diagnostics_off.grid_time):
        raise ValueError("Trend-method diagnostics must use the same grid time vector.")
    if not np.array_equal(diagnostics_on.years, diagnostics_off.years):
        raise ValueError("Trend-method diagnostics must use the same yearly time vector.")


if __name__ == "__main__":
    main()
