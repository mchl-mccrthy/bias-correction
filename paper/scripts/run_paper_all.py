from __future__ import annotations

from collections.abc import Callable

from eqtm import BiasCorrectionConfig, biascorrect, makediagnostics, makeplots
from paper.scripts.compare_matlab_python import check_matlab, main as compare_matlab_python
from paper.scripts.cross_validation import main as cross_validation
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on
from paper.scripts.make_outputs import main as make_outputs


def main() -> None:
    matlab_executable = check_matlab()
    config_functions: list[Callable[[], BiasCorrectionConfig]] = [
        config_switzerland_tas_trends_on,
        config_switzerland_tas_trends_off,
        config_switzerland_pr_trends_on,
        config_switzerland_pr_trends_off,
    ]

    for make_config in config_functions:
        _run_config(make_config())

    compare_matlab_python(matlab_executable)
    cross_validation()
    make_outputs()


def _run_config(cfg: BiasCorrectionConfig) -> None:
    biascorrect(cfg)
    diagnostics = makediagnostics(cfg)
    makeplots(diagnostics, cfg)


if __name__ == "__main__":
    main()
