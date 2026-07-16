from __future__ import annotations

from eqm_step import makediagnostics, makeplots, runbiascorrection
from scripts.config_andermatt_zuerich_pr import config_andermatt_zuerich_pr


def main() -> None:
    cfg = config_andermatt_zuerich_pr()

    runbiascorrection(cfg)
    diagnostics = makediagnostics(cfg)
    makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
