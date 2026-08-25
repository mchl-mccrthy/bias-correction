from __future__ import annotations

from collections.abc import Callable

from eqtm import BiasCorrectionConfig, biascorrect, makediagnostics, makeplots
from paper.scripts.cross_validate_paper import main as cross_validate_paper
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on
from paper.scripts.make_paper_annual_mae import main as make_paper_annual_mae
from paper.scripts.make_paper_diagnostics_table import main as make_paper_diagnostics_table
from paper.scripts.make_paper_locator_map import main as make_paper_locator_map
from paper.scripts.make_paper_maps import main as make_paper_maps
from paper.scripts.make_paper_qm_residuals import main as make_paper_qm_residuals
from paper.scripts.make_paper_qq import main as make_paper_qq
from paper.scripts.make_paper_quantile_mae import main as make_paper_quantile_mae
from paper.scripts.make_paper_trend_mae import main as make_paper_trend_mae
from paper.scripts.make_paper_trends import main as make_paper_trends


def main() -> None:
    config_functions: list[Callable[[], BiasCorrectionConfig]] = [
        config_switzerland_tas_trends_on,
        config_switzerland_tas_trends_off,
        config_switzerland_pr_trends_on,
        config_switzerland_pr_trends_off,
    ]

    for make_config in config_functions:
        _run_config(make_config())

    cross_validate_paper()
    _make_paper_outputs()


def _run_config(cfg: BiasCorrectionConfig) -> None:
    biascorrect(cfg)
    diagnostics = makediagnostics(cfg)
    makeplots(diagnostics, cfg)


def _make_paper_outputs() -> None:
    make_paper_maps()
    make_paper_locator_map()
    make_paper_qq()
    make_paper_qm_residuals()
    make_paper_annual_mae()
    make_paper_quantile_mae()
    make_paper_trend_mae()
    make_paper_trends()
    make_paper_diagnostics_table()


if __name__ == "__main__":
    main()
