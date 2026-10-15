from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import theilsenslope
from eqtm.plotting import (
    MARKER_SIZE,
    _format_units,
    _new_figure,
    _remove_terminal_inverse_timestep,
    _save_figure,
    _set_plot_style,
)
from paper.scripts.config_switzerland_pr_trends_off import config_switzerland_pr_trends_off
from paper.scripts.config_switzerland_pr_trends_on import config_switzerland_pr_trends_on
from paper.scripts.config_switzerland_tas_trends_off import config_switzerland_tas_trends_off
from paper.scripts.config_switzerland_tas_trends_on import config_switzerland_tas_trends_on
from paper.scripts.diagnostics_cache import makediagnostics_cached as makediagnostics
from paper.scripts.make_annual_mae_plots import _check_matching_diagnostics
from paper.scripts.make_qq_plots import OFF_COLOR, ON_COLOR, RAW_COLOR


SEASONS = {
    "MAM": (3, 4, 5),
    "JJA": (6, 7, 8),
    "SON": (9, 10, 11),
    "DJF": (12, 1, 2),
}
SEASON_ORDER = ["DJF", "MAM", "JJA", "SON"]
MIN_SEASON_COMPLETENESS = 0.90
METHODS = [
    "Raw",
    "Bias-corrected, trend mapping on",
    "Bias-corrected, trend mapping off",
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper" / "figures_and_tables"
    figure_dir.mkdir(parents=True, exist_ok=True)
    _set_plot_style()

    tas_cfg = config_switzerland_tas_trends_on()
    pr_cfg = config_switzerland_pr_trends_on()
    tas_table = make_seasonal_trend_plots(
        tas_cfg,
        config_switzerland_tas_trends_off(),
        figure_dir,
    )
    pr_table = make_seasonal_trend_plots(
        pr_cfg,
        config_switzerland_pr_trends_off(),
        figure_dir,
    )
    pd.concat(
        [tas_table, pr_table],
        axis=1,
        keys=[tas_cfg.clim_var_long_name, pr_cfg.clim_var_long_name],
    ).to_csv(figure_dir / "seasonal_trend_mae.csv", float_format="%.3g")


def make_seasonal_trend_plots(
    cfg_on: BiasCorrectionConfig,
    cfg_off: BiasCorrectionConfig,
    figure_dir: Path,
) -> pd.DataFrame:
    """Plot seasonal trend MAE and return its paper-table values."""
    diagnostics_on = makediagnostics(cfg_on)
    diagnostics_off = makediagnostics(cfg_off)
    _check_matching_diagnostics(diagnostics_on, diagnostics_off)
    station = diagnostics_on.station_clim_var
    raw = diagnostics_on.raw_station_clim_var
    bc_on = diagnostics_on.bc_station_clim_var
    bc_off = diagnostics_off.bc_station_clim_var
    time = diagnostics_on.grid_time
    summary = pd.DataFrame(index=METHODS)

    for season in SEASONS:
        years, seasonal = makeseasonaltables(
            station, raw, bc_on, bc_off, time, season, cfg_on.agg_method
        )
        station_slopes, raw_slopes, on_slopes, off_slopes = _seasonalslopes(
            years, seasonal
        )
        unit = _plain_units(_seasonaltrendunits(cfg_on))
        summary[f"MAE trend {season} ({unit})"] = [
            _trendmae(station_slopes, modelled)
            for modelled in (raw_slopes, on_slopes, off_slopes)
        ]
    _plotseasonaltrendmae(
        summary,
        cfg_on,
        figure_dir / f"{cfg_on.clim_var_name}_seasonal_trend_mae.png",
    )
    return summary


def makeseasonaltables(
    station: pd.DataFrame,
    raw: pd.DataFrame,
    bc_on: pd.DataFrame,
    bc_off: pd.DataFrame,
    time: pd.DatetimeIndex,
    season: str,
    agg_method: str,
) -> tuple[np.ndarray, list[pd.DataFrame]]:
    """Aggregate complete daily seasons, assigning December to the next DJF."""
    if season not in SEASONS:
        raise ValueError(f"Unknown season: {season}")
    if agg_method not in {"mean", "sum"}:
        raise ValueError("agg_method must be 'mean' or 'sum'.")

    season_year = time.year.to_numpy(copy=True)
    if season == "DJF":
        season_year = season_year + (time.month == 12).astype(int)
    in_season = np.isin(time.month, SEASONS[season])
    candidate_years = np.unique(season_year[in_season])
    tables = [station, raw, bc_on, bc_off]
    outputs = [pd.DataFrame(np.nan, index=candidate_years, columns=station.columns) for _ in tables]

    for year in candidate_years:
        mask = in_season & (season_year == year)
        if not _is_complete_daily_season(time[mask], int(year), season):
            continue
        for i_station, column in enumerate(station.columns):
            values = [table.loc[mask, column].to_numpy(dtype=float) for table in tables]
            valid = np.logical_and.reduce([np.isfinite(value) for value in values])
            completeness = np.count_nonzero(valid) / values[0].size
            if completeness < MIN_SEASON_COMPLETENESS:
                continue
            for output, value in zip(outputs, values):
                valid_values = value[valid]
                aggregate = np.mean(valid_values)
                if agg_method == "sum":
                    aggregate = np.sum(valid_values) / completeness
                output.iloc[output.index.get_loc(year), i_station] = (
                    aggregate
                )

    return candidate_years, outputs


def _is_complete_daily_season(
    times: pd.DatetimeIndex,
    season_year: int,
    season: str,
) -> bool:
    if season == "DJF":
        start = pd.Timestamp(season_year - 1, 12, 1)
        end = pd.Timestamp(season_year, 2, 1) + pd.offsets.MonthEnd(1)
    else:
        start = pd.Timestamp(season_year, SEASONS[season][0], 1)
        end = pd.Timestamp(season_year, SEASONS[season][-1], 1) + pd.offsets.MonthEnd(1)
    expected = pd.date_range(start, end, freq="D")
    return len(times) == len(expected) and np.array_equal(times.to_numpy(), expected.to_numpy())


def _seasonalslopes(
    years: np.ndarray,
    tables: list[pd.DataFrame],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    slopes = [np.full(tables[0].shape[1], np.nan) for _ in tables]
    for i_station in range(tables[0].shape[1]):
        values = [table.iloc[:, i_station].to_numpy(dtype=float) for table in tables]
        valid = np.logical_and.reduce([np.isfinite(value) for value in values])
        if np.count_nonzero(valid) >= 2:
            for output, value in zip(slopes, values):
                output[i_station] = theilsenslope(years[valid], value[valid])
    return tuple(slopes)


def _plotseasonaltrendmae(
    summary: pd.DataFrame,
    cfg: BiasCorrectionConfig,
    path: Path,
) -> None:
    fig, ax = _new_figure(4, 2 * 4 / 3, 5)
    units = _seasonaltrendunits(cfg)
    plain_units = _plain_units(units)
    y = np.arange(len(SEASON_ORDER), dtype=float)
    offsets = (-0.14, 0.0, 0.14)
    colors = (RAW_COLOR, ON_COLOR, OFF_COLOR)
    handles = []
    for method, offset, color in zip(METHODS, offsets, colors):
        values = [
            summary.loc[method, f"MAE trend {season} ({plain_units})"]
            for season in SEASON_ORDER
        ]
        handles.append(
            ax.scatter(values, y + offset, color=color, s=MARKER_SIZE, zorder=2)
        )

    ax._eqtm_categorical_y = True
    ax.set_yticks(y)
    ax.set_yticklabels(SEASON_ORDER)
    ax.set_ylim(len(SEASON_ORDER) - 0.5, -0.5)
    ax.set_xlim(left=0)
    ax.set_xlabel(f"MAE, {cfg.clim_var_long_name.lower()} trend ({units})")
    ax.legend(
        handles,
        METHODS,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        borderaxespad=0,
        ncol=1,
    )
    _save_figure(fig, path)


def _seasonaltrendunits(cfg: BiasCorrectionConfig) -> str:
    native = cfg.clim_var_units
    if cfg.agg_method == "sum":
        units = _format_units(_remove_terminal_inverse_timestep(native))
        return f"{units} season$^{{-1}}$ year$^{{-1}}$"
    units = _format_units(native)
    return f"{units} year$^{{-1}}$"


def _trendmae(observed: np.ndarray, modelled: np.ndarray) -> float:
    valid = np.isfinite(observed) & np.isfinite(modelled)
    if not np.any(valid):
        return float("nan")
    return float(np.mean(np.abs(modelled[valid] - observed[valid])))


def _plain_units(units: str) -> str:
    return units.replace("$", "").replace("{", "").replace("}", "")


if __name__ == "__main__":
    main()
