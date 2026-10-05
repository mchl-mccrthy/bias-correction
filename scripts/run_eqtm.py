from __future__ import annotations

from eqtm import biascorrect, makediagnostics, makeplots
from scripts.config_andermatt_zurich_tas import config_andermatt_zurich_tas


def main() -> None:
    cfg = config_andermatt_zurich_tas()

    biascorrect(cfg)
    diagnostics = makediagnostics(cfg)
    makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
