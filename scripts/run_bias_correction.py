from __future__ import annotations

from eqm_step import makediagnostics, makeplots, runbiascorrection
from scripts.config_andermatt_zuerich_tas import config_andermatt_zuerich_tas


def main() -> None:
    cfg = config_andermatt_zuerich_tas()

    runbiascorrection(cfg)
    diagnostics = makediagnostics(cfg)
    makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
