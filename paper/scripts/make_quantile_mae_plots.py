from __future__ import annotations

from pathlib import Path

from eqtm.config import BiasCorrectionConfig
from eqtm.plotting import _format_units, _new_figure, _save_figure, _set_plot_style, _stripplot
from paper.scripts.diagnostics_cache import makediagnostics_cached as makediagnostics
from paper.scripts.make_annual_mae_plots import _check_matching_diagnostics
from paper.scripts.make_qq_plots import OFF_COLOR, ON_COLOR, RAW_COLOR
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures_and_tables"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    _paper_quantile_mae(
        config_switzerland_tas_trends_on(),
        config_switzerland_tas_trends_off(),
        figure_dir,
    )
    _paper_quantile_mae(
        config_switzerland_pr_trends_on(),
        config_switzerland_pr_trends_off(),
        figure_dir,
    )


def _paper_quantile_mae(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
    figure_dir: Path,
) -> None:
    diagnostics_on = makediagnostics(cfg_on)
    diagnostics_off = makediagnostics(cfg_off)
    _check_matching_diagnostics(diagnostics_on, diagnostics_off)

    fig, ax = _new_figure(4, 2, 5)
    _stripplot(
        ax,
        [
            diagnostics_on.raw_station_quantile_mae,
            diagnostics_on.bc_station_quantile_mae,
            diagnostics_off.bc_station_quantile_mae,
        ],
        [
            "Raw",
            "Bias-corrected, trend mapping on",
            "Bias-corrected, trend mapping off",
        ],
        [RAW_COLOR, ON_COLOR, OFF_COLOR],
    )
    ax.set_xlabel(
        f"MAE, {cfg_on.clim_var_long_name.lower()} quantiles ({_format_units(cfg_on.clim_var_units)})"
    )
    _save_figure(fig, figure_dir / f"{cfg_on.clim_var_name}_quantile_mae_strip.png")


if __name__ == "__main__":
    main()
