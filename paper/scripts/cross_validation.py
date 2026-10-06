from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from eqtm import BiasCorrectionConfig, biascorrect
from eqtm.diagnostics import (
    diagnosticcsvtable,
    diagnosticunits,
    getannualmae,
    gettheilsenslopes,
    getquantilemae,
    gridtostations,
    makeyearlytables,
)
from eqtm.io import loadgriddata, loadstationdata
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on


N_FOLDS = 5


def main() -> None:
    config_pairs = [
        (
            config_switzerland_tas_trends_on(),
            config_switzerland_tas_trends_off(),
        ),
        (
            config_switzerland_pr_trends_on(),
            config_switzerland_pr_trends_off(),
        ),
    ]

    rows = []
    for cfg_on, cfg_off in config_pairs:
        rows.extend(_crossvalidatevariable(cfg_on, cfg_off))

    cv_dir = _cvroot(config_pairs[0][0])
    cv_dir.mkdir(parents=True, exist_ok=True)
    folds = pd.DataFrame(rows)
    configs = [pair[0] for pair in config_pairs]
    _fold_export(folds, configs).to_csv(cv_dir / "switzerland_cross_validation_folds.csv", index=False)
    summary = _summarise(folds, configs)
    summary.to_csv(cv_dir / "switzerland_cross_validation_summary.csv")
    paper_dir = Path(__file__).resolve().parents[1] / "figures_and_tables"
    paper_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(paper_dir / "switzerland_cross_validation_summary.csv")


def _crossvalidatevariable(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
) -> list[dict[str, float | str | int]]:
    station_input = pd.read_csv(cfg_on.file_path_station_clim_var)
    station = loadstationdata(cfg_on.file_path_station_clim_var, cfg_on.file_path_station_coords)
    raw = loadgriddata(cfg_on.file_path_raw_data, cfg_on.clim_var_name)
    raw_at_stations = gridtostations(raw.clim_var, station.x, station.y, raw.x, raw.y, station.clim_var)

    rows = []
    folds = _stationfolds(list(station.clim_var.columns), N_FOLDS)
    for i_fold, validation_stations in enumerate(folds, start=1):
        print(
            f"{cfg_on.clim_var_name}: fold {i_fold}/{N_FOLDS}; "
            f"withholding {len(validation_stations)} stations",
            flush=True,
        )
        station_train_file = _writetrainingstations(
            station_input,
            validation_stations,
            _cvroot(cfg_on) / cfg_on.clim_var_name / "station_training_files",
            cfg_on.clim_var_name,
            i_fold,
        )
        rows.extend(
            _evaluatestations(
                cfg_on.clim_var_name,
                "Raw",
                i_fold,
                validation_stations,
                station,
                raw_at_stations,
                raw_at_stations,
                raw.time,
                cfg_on.agg_method,
            )
        )

        for label, cfg in (
            ("Bias-corrected, trend mapping on", cfg_on),
            ("Bias-corrected, trend mapping off", cfg_off),
        ):
            cfg_cv = _foldconfig(cfg, station_train_file, i_fold)
            print(f"{cfg.clim_var_name}: fold {i_fold}/{N_FOLDS}; {label}", flush=True)
            biascorrect(cfg_cv)
            bc = loadgriddata(cfg_cv.file_path_bc_data, cfg_cv.clim_var_name)
            bc_at_stations = gridtostations(bc.clim_var, station.x, station.y, raw.x, raw.y, station.clim_var)
            rows.extend(
                _evaluatestations(
                    cfg.clim_var_name,
                    label,
                    i_fold,
                    validation_stations,
                    station,
                    raw_at_stations,
                    bc_at_stations,
                    raw.time,
                    cfg.agg_method,
                )
            )
    return rows


def _stationfolds(station_names: list[str], n_folds: int) -> list[list[str]]:
    return [list(fold) for fold in np.array_split(np.array(station_names, dtype=object), n_folds)]


def _writetrainingstations(
    station_input: pd.DataFrame,
    validation_stations: list[str],
    output_dir: Path,
    clim_var_name: str,
    i_fold: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    train = station_input.drop(columns=validation_stations)
    output_file = output_dir / f"{clim_var_name}_fold_{i_fold:02d}_train.csv"
    train.to_csv(output_file, index=False)
    return output_file


def _foldconfig(
    cfg: BiasCorrectionConfig,
    station_train_file: Path,
    i_fold: int,
) -> BiasCorrectionConfig:
    method_dir = "trend_mapping_on" if cfg.trend_mapping else "trend_mapping_off"
    output_dir = _cvroot(cfg) / cfg.clim_var_name / method_dir / f"fold_{i_fold:02d}"
    output_file = output_dir / f"{cfg.clim_var_name}_bc_{method_dir}_fold_{i_fold:02d}.nc"
    figures_tables_dir = output_dir / "figures_and_tables"
    return replace(
        cfg,
        file_path_station_clim_var=station_train_file,
        file_path_bc_data=output_file,
        file_path_figures_tables=figures_tables_dir,
    )


def _evaluatestations(
    clim_var_name: str,
    method: str,
    i_fold: int,
    station_names: list[str],
    station,
    raw_at_stations: pd.DataFrame,
    model_at_stations: pd.DataFrame,
    time: pd.DatetimeIndex,
    agg_method: str,
) -> list[dict[str, float | str | int]]:
    rows = []
    for station_name in station_names:
        rows.append(
            _evaluatemetrics(
                clim_var_name,
                method,
                i_fold,
                station_name,
                station.clim_var[[station_name]],
                raw_at_stations[[station_name]],
                model_at_stations[[station_name]],
                time,
                agg_method,
            )
        )
    return rows


def _evaluatemetrics(
    clim_var_name: str,
    method: str,
    i_fold: int,
    station_name: str,
    station_values: pd.DataFrame,
    raw_values: pd.DataFrame,
    model_values: pd.DataFrame,
    time: pd.DatetimeIndex,
    agg_method: str,
) -> dict[str, float | str | int]:
    station_yearly, raw_yearly, model_yearly, years = makeyearlytables(
        station_values,
        raw_values,
        model_values,
        time,
        agg_method,
    )
    station_slope, _, model_slope = gettheilsenslopes(
        station_yearly, raw_yearly, model_yearly, years
    )
    _, model_quantile_mae = getquantilemae(station_values, raw_values, model_values)
    _, model_yearly_mae = getannualmae(station_yearly, raw_yearly, model_yearly)

    return {
        "Variable": clim_var_name,
        "Method": method,
        "Fold": i_fold,
        "Station": station_name,
        "MAE quantiles": model_quantile_mae[0],
        "MAE yearly": model_yearly_mae[0],
        "Station trend": station_slope[0],
        "Model trend": model_slope[0],
        "MAE trends": abs(model_slope[0] - station_slope[0]),
    }


def _fold_export(folds: pd.DataFrame, configs: list[BiasCorrectionConfig]) -> pd.DataFrame:
    """Keep mixed-variable rows together, with units explicit for each metric group."""
    table = folds.rename(columns={"MAE trends": "AE trend"}).copy()
    units = {cfg.clim_var_name: diagnosticunits(cfg) for cfg in configs}
    for i, name in enumerate(["Quantile units", "Yearly units", "Trend units"]):
        table[name] = table["Variable"].map({variable: values[i] for variable, values in units.items()})
    return table


def _summarise(folds: pd.DataFrame, configs: list[BiasCorrectionConfig]) -> pd.DataFrame:
    metrics = ["MAE quantiles", "MAE yearly", "MAE trends"]
    methods = ["Raw", "Bias-corrected, trend mapping on", "Bias-corrected, trend mapping off"]
    means = folds.groupby(["Variable", "Method"])[metrics].mean()
    table = pd.concat(
        [diagnosticcsvtable(means.loc[cfg.clim_var_name].reindex(methods), cfg) for cfg in configs],
        axis=1,
        keys=[cfg.clim_var_long_name for cfg in configs],
    )
    table.index.name = None
    return table


def _cvroot(cfg: BiasCorrectionConfig) -> Path:
    return Path(cfg.file_path_bc_data).parent.parent / "cross_validation"


if __name__ == "__main__":
    main()
