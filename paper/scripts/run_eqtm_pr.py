from __future__ import annotations

from eqtm import biascorrect, makediagnostics, makeplots
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on


def main() -> None:
    for make_config in (config_switzerland_pr_trends_on, config_switzerland_pr_trends_off):
        cfg = make_config()
        biascorrect(cfg)
        diagnostics = makediagnostics(cfg)
        makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
