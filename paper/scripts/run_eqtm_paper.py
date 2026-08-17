from __future__ import annotations

from collections.abc import Callable

from eqtm import BiasCorrectionConfig, biascorrect, makediagnostics, makeplots
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


def main() -> None:
    config_functions: list[Callable[[], BiasCorrectionConfig]] = [
        config_switzerland_tas_trends_on,
        config_switzerland_tas_trends_off,
        config_switzerland_pr_trends_on,
        config_switzerland_pr_trends_off,
    ]

    for make_config in config_functions:
        _run_config(make_config())


def _run_config(cfg: BiasCorrectionConfig) -> None:
    biascorrect(cfg)
    diagnostics = makediagnostics(cfg)
    makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
