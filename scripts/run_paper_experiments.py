from __future__ import annotations

from collections.abc import Callable

from eqtm import BiasCorrectionConfig, biascorrect, makediagnostics, makeplots
from scripts.config_andermatt_zuerich_pr_trends_off import config_andermatt_zuerich_pr_trends_off
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_off import config_andermatt_zuerich_tas_trends_off
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


def main() -> None:
    config_functions: list[Callable[[], BiasCorrectionConfig]] = [
        config_andermatt_zuerich_tas_trends_on,
        config_andermatt_zuerich_tas_trends_off,
        config_andermatt_zuerich_pr_trends_on,
        config_andermatt_zuerich_pr_trends_off,
    ]

    for make_config in config_functions:
        cfg = make_config()
        biascorrect(cfg)
        diagnostics = makediagnostics(cfg)
        makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
