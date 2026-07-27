from __future__ import annotations

from pathlib import Path

import pandas as pd

from eqtm import makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from paper.scripts.make_paper_annual_mae import _check_matching_diagnostics
from scripts.config_andermatt_zuerich_pr_trends_off import config_andermatt_zuerich_pr_trends_off
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_off import config_andermatt_zuerich_tas_trends_off
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


METRIC_COLUMNS = ["MAE quantiles", "MAE yearly", "r2 trends"]
ROW_LABELS = ["Raw", "Bias-corrected, trend mapping on", "Bias-corrected, trend mapping off"]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    tas_on = makediagnostics(config_andermatt_zuerich_tas_trends_on())
    tas_off = makediagnostics(config_andermatt_zuerich_tas_trends_off())
    pr_on = makediagnostics(config_andermatt_zuerich_pr_trends_on())
    pr_off = makediagnostics(config_andermatt_zuerich_pr_trends_off())

    table = _paper_diagnostics_table(
        config_andermatt_zuerich_tas_trends_on(),
        tas_on,
        tas_off,
        config_andermatt_zuerich_pr_trends_on(),
        pr_on,
        pr_off,
    )
    table.to_csv(figure_dir / "diagnostics_summary.csv", float_format="%.3g")


def _paper_diagnostics_table(
    cfg_tas: BiasCorrectionConfig,
    diagnostics_tas_on: Diagnostics,
    diagnostics_tas_off: Diagnostics,
    cfg_pr: BiasCorrectionConfig,
    diagnostics_pr_on: Diagnostics,
    diagnostics_pr_off: Diagnostics,
) -> pd.DataFrame:
    _check_matching_diagnostics(diagnostics_tas_on, diagnostics_tas_off)
    _check_matching_diagnostics(diagnostics_pr_on, diagnostics_pr_off)

    return pd.concat(
        [
            _variable_summary(diagnostics_tas_on, diagnostics_tas_off),
            _variable_summary(diagnostics_pr_on, diagnostics_pr_off),
        ],
        axis=1,
        keys=[cfg_tas.clim_var_long_name, cfg_pr.clim_var_long_name],
    )


def _variable_summary(diagnostics_on: Diagnostics, diagnostics_off: Diagnostics) -> pd.DataFrame:
    on_table = diagnostics_on.summary_table.set_index("Dataset")
    off_table = diagnostics_off.summary_table.set_index("Dataset")
    return pd.DataFrame(
        [
            on_table.loc["Raw", METRIC_COLUMNS],
            on_table.loc["Bias-corrected", METRIC_COLUMNS],
            off_table.loc["Bias-corrected", METRIC_COLUMNS],
        ],
        index=ROW_LABELS,
        columns=METRIC_COLUMNS,
    )


if __name__ == "__main__":
    main()
