from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import BiasCorrectionConfig
from .io import loadgriddata, loadstationdata
from .spatial import indexofclosest2, spatialmean


@dataclass
class Diagnostics:
    """Diagnostic data used to evaluate and plot the bias-correction workflow."""

    station_clim_var: pd.DataFrame
    station_coords: pd.DataFrame
    station_x: np.ndarray
    station_y: np.ndarray
    station_time: pd.DatetimeIndex
    raw_station_clim_var: pd.DataFrame
    bc_station_clim_var: pd.DataFrame
    station_clim_var_yearly: pd.DataFrame
    raw_station_clim_var_yearly: pd.DataFrame
    bc_station_clim_var_yearly: pd.DataFrame
    years: np.ndarray
    station_theil_sen_slopes: np.ndarray
    raw_station_theil_sen_slopes: np.ndarray
    bc_station_theil_sen_slopes: np.ndarray
    raw_station_quantile_mae: np.ndarray
    bc_station_quantile_mae: np.ndarray
    raw_station_annual_mae: np.ndarray
    bc_station_annual_mae: np.ndarray
    summary_table: pd.DataFrame
    raw_grid_domain_mean: np.ndarray
    bc_grid_domain_mean: np.ndarray
    raw_grid_clim_var_yearly: np.ndarray
    bc_grid_clim_var_yearly: np.ndarray
    bc_grid_theil_sen_slopes: np.ndarray
    grid_x: np.ndarray
    grid_y: np.ndarray
    grid_time: pd.DatetimeIndex


def makediagnostics(cfg: BiasCorrectionConfig) -> Diagnostics:
    """Compute diagnostic summaries from raw, station, and corrected data.

    This function reloads the input and bias-corrected datasets, extracts raw
    and corrected grid values at station locations, creates annual station and
    grid summaries, and estimates Theil-Sen slopes for diagnostic plots.
    """

    if not Path(cfg.file_path_bc_data).is_file():
        raise FileNotFoundError(f"Bias-corrected data file not found: {cfg.file_path_bc_data}")

    raw = loadgriddata(cfg.file_path_raw_data, cfg.clim_var_name)
    bc = loadgriddata(cfg.file_path_bc_data, cfg.clim_var_name)
    station = loadstationdata(cfg.file_path_station_clim_var, cfg.file_path_station_coords)

    raw_station = gridtostations(raw.clim_var, station.x, station.y, raw.x, raw.y, station.clim_var)
    bc_station = gridtostations(bc.clim_var, station.x, station.y, raw.x, raw.y, station.clim_var)

    station_yearly, raw_station_yearly, bc_station_yearly, years = makeyearlytables(
        station.clim_var, raw_station, bc_station, raw.time, cfg.agg_method
    )
    station_slopes, raw_slopes, bc_slopes = gettheilsenslopes(
        station_yearly, raw_station_yearly, bc_station_yearly, years
    )
    raw_quantile_mae, bc_quantile_mae = getquantilemae(station.clim_var, raw_station, bc_station)
    raw_annual_mae, bc_annual_mae = getannualmae(station_yearly, raw_station_yearly, bc_station_yearly)
    station_means, raw_means, bc_means = getstationmeans(station_yearly, raw_station_yearly, bc_station_yearly)
    raw_grid_domain_mean = spatialmean(raw.clim_var, raw.y, cfg.coordinate_system)
    bc_grid_domain_mean = spatialmean(bc.clim_var, raw.y, cfg.coordinate_system)
    raw_grid_yearly, grid_years = makeyearlygrid(raw.clim_var, raw.time, cfg.agg_method)
    bc_grid_yearly, _ = makeyearlygrid(bc.clim_var, raw.time, cfg.agg_method)
    summary_inputs = (
        station_slopes,
        raw_slopes,
        bc_slopes,
        raw_quantile_mae,
        bc_quantile_mae,
        raw_annual_mae,
        bc_annual_mae,
        station_means,
        raw_means,
        bc_means,
    )
    summary_table = makesummarytable(cfg.clim_var_name, *summary_inputs)
    summary_table = summary_table.drop(columns=[
        "Observed mean", "Model mean", "Observed trend", "Model trend",
    ])
    domain_stats = [
        getdomainsummary(grid, grid_years, raw.y, cfg.coordinate_system)
        for grid in (raw_grid_yearly, bc_grid_yearly)
    ]
    summary_table["Domain mean yearly"] = [stats[0] for stats in domain_stats]
    summary_table["Domain trend"] = [stats[1] for stats in domain_stats]
    savediagnosticsummarytable(diagnosticcsvtable(summary_table, cfg), cfg.file_path_figures_tables, cfg.clim_var_name)
    station_dir = Path(cfg.file_path_figures_tables) / "individual_stations"
    station_dir.mkdir(parents=True, exist_ok=True)
    for i, station_name in enumerate(station.clim_var.columns):
        table = makesummarytable(cfg.clim_var_name, *(values[i:i + 1] for values in summary_inputs))
        table = table.rename(columns={"MAE trends": "AE trend",
                                      "Observed mean": "Observed mean yearly",
                                      "Model mean": "Model mean yearly"})
        table.insert(1, "Station", station_name)
        diagnosticcsvtable(table, cfg).to_csv(
            station_dir / f"{station_name}_{cfg.clim_var_name}_diagnostics_summary.csv", index=False)
    bc_grid_slopes = theilsenslope(grid_years, bc_grid_yearly, axis=2)

    return Diagnostics(
        station.clim_var,
        station.coords,
        station.x,
        station.y,
        station.time,
        raw_station,
        bc_station,
        station_yearly,
        raw_station_yearly,
        bc_station_yearly,
        years,
        station_slopes,
        raw_slopes,
        bc_slopes,
        raw_quantile_mae,
        bc_quantile_mae,
        raw_annual_mae,
        bc_annual_mae,
        summary_table,
        raw_grid_domain_mean,
        bc_grid_domain_mean,
        raw_grid_yearly,
        bc_grid_yearly,
        bc_grid_slopes,
        raw.x,
        raw.y,
        raw.time,
    )


def gridtostations(
    clim_var: np.ndarray,
    station_x: np.ndarray,
    station_y: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    template_table: pd.DataFrame,
) -> pd.DataFrame:
    rows, cols = indexofclosest2(station_x, station_y, grid_x, grid_y)
    out = pd.DataFrame(np.nan, index=template_table.index, columns=template_table.columns)
    for i_station in range(len(station_x)):
        out.iloc[:, i_station] = clim_var[rows[i_station], cols[i_station], :]
    return out


def makeyearlytables(
    station_clim_var: pd.DataFrame,
    raw_station_clim_var: pd.DataFrame,
    bc_station_clim_var: pd.DataFrame,
    grid_time: pd.DatetimeIndex,
    agg_method: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    min_year_completeness = 0.90
    years = np.unique(grid_time.year)
    yearly = [
        pd.DataFrame(np.nan, index=years, columns=station_clim_var.columns),
        pd.DataFrame(np.nan, index=years, columns=raw_station_clim_var.columns),
        pd.DataFrame(np.nan, index=years, columns=bc_station_clim_var.columns),
    ]

    for year in years:
        ind_year = grid_time.year == year
        for i_station, column in enumerate(station_clim_var.columns):
            station_tmp = station_clim_var.loc[ind_year, column].to_numpy()
            completeness = np.sum(~np.isnan(station_tmp)) / len(station_tmp)
            if completeness >= min_year_completeness:
                if agg_method == "sum":
                    reducer = np.nansum
                elif agg_method == "mean":
                    reducer = np.nanmean
                else:
                    raise ValueError("agg_method must be 'sum' or 'mean'.")
                yearly[0].loc[year, column] = reducer(station_clim_var.loc[ind_year, column])
                yearly[1].loc[year, column] = reducer(raw_station_clim_var.loc[ind_year, column])
                yearly[2].loc[year, column] = reducer(bc_station_clim_var.loc[ind_year, column])

    return yearly[0], yearly[1], yearly[2], years


def makeyearlygrid(
    grid_clim_var: np.ndarray,
    grid_time: pd.DatetimeIndex,
    agg_method: str,
) -> tuple[np.ndarray, np.ndarray]:
    years = np.unique(grid_time.year)
    yearly = np.full((*grid_clim_var.shape[:2], len(years)), np.nan, dtype=grid_clim_var.dtype)
    for i_year, year in enumerate(years):
        ind_year = grid_time.year == year
        if agg_method == "sum":
            yearly[:, :, i_year] = np.nansum(grid_clim_var[:, :, ind_year], axis=2)
        elif agg_method == "mean":
            yearly[:, :, i_year] = np.nanmean(grid_clim_var[:, :, ind_year], axis=2)
        else:
            raise ValueError("agg_method must be 'sum' or 'mean'.")
    return yearly, years


def theilsenslope(
    x: np.ndarray,
    y: np.ndarray,
    axis: int = -1,
    chunk_size: int = 5000,
) -> float | np.ndarray:
    """Median pairwise slope along an axis, evaluated in bounded-memory chunks."""
    x = np.asarray(x, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float)
    if axis < 0:
        axis += y.ndim
    if axis < 0 or axis >= y.ndim:
        raise ValueError("axis is outside the dimensions of y.")
    if y.shape[axis] != x.size:
        raise ValueError("The selected y axis must have the same length as x.")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    moved = np.moveaxis(y, axis, -1)
    output_shape = moved.shape[:-1]
    flat = moved.reshape(-1, x.size)
    finite_x = np.isfinite(x)
    x = x[finite_x]
    flat = flat[:, finite_x]
    out = np.full(flat.shape[0], np.nan, dtype=float)
    if x.size < 2:
        result = out.reshape(output_shape)
        return result.item() if result.ndim == 0 else result

    first, second = np.triu_indices(x.size, k=1)
    dx = x[second] - x[first]
    distinct = dx != 0
    first = first[distinct]
    second = second[distinct]
    dx = dx[distinct]
    if dx.size:
        for start in range(0, flat.shape[0], chunk_size):
            stop = min(start + chunk_size, flat.shape[0])
            block = flat[start:stop]
            eligible = np.sum(np.isfinite(block), axis=1) >= 2
            if not np.any(eligible):
                continue
            values = block[eligible]
            pairwise = (values[:, second] - values[:, first]) / dx
            block_out = out[start:stop]
            has_slope = np.any(np.isfinite(pairwise), axis=1)
            eligible_indices = np.flatnonzero(eligible)
            block_out[eligible_indices[has_slope]] = np.nanmedian(
                pairwise[has_slope], axis=1
            )

    result = out.reshape(output_shape)
    return result.item() if result.ndim == 0 else result


def gettheilsenslopes(
    station_clim_var_yearly: pd.DataFrame,
    raw_station_clim_var_yearly: pd.DataFrame,
    bc_station_clim_var_yearly: pd.DataFrame,
    years: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_stations = station_clim_var_yearly.shape[1]
    station_slopes = np.full(n_stations, np.nan)
    raw_slopes = np.full(n_stations, np.nan)
    bc_slopes = np.full(n_stations, np.nan)
    for i_station in range(n_stations):
        station_tmp = station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        raw_tmp = raw_station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        bc_tmp = bc_station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        valid = ~np.isnan(station_tmp) & ~np.isnan(raw_tmp) & ~np.isnan(bc_tmp)
        if np.sum(valid) >= 2:
            station_slopes[i_station] = theilsenslope(years[valid], station_tmp[valid])
            raw_slopes[i_station] = theilsenslope(years[valid], raw_tmp[valid])
            bc_slopes[i_station] = theilsenslope(years[valid], bc_tmp[valid])
    return station_slopes, raw_slopes, bc_slopes


def getannualmae(
    station_clim_var_yearly: pd.DataFrame,
    raw_station_clim_var_yearly: pd.DataFrame,
    bc_station_clim_var_yearly: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    n_stations = station_clim_var_yearly.shape[1]
    raw_mae = np.full(n_stations, np.nan)
    bc_mae = np.full(n_stations, np.nan)
    for i_station in range(n_stations):
        station_tmp = station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        raw_tmp = raw_station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        bc_tmp = bc_station_clim_var_yearly.iloc[:, i_station].to_numpy(dtype=float)
        valid = ~np.isnan(station_tmp) & ~np.isnan(raw_tmp) & ~np.isnan(bc_tmp)
        if np.any(valid):
            raw_mae[i_station] = np.nanmean(np.abs(raw_tmp[valid] - station_tmp[valid]))
            bc_mae[i_station] = np.nanmean(np.abs(bc_tmp[valid] - station_tmp[valid]))
    return raw_mae, bc_mae


def getquantilemae(
    station_clim_var: pd.DataFrame,
    raw_station_clim_var: pd.DataFrame,
    bc_station_clim_var: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    n_stations = station_clim_var.shape[1]
    raw_mae = np.full(n_stations, np.nan)
    bc_mae = np.full(n_stations, np.nan)
    qs = np.linspace(0, 1, 1000)
    for i_station in range(n_stations):
        station_tmp = station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
        raw_tmp = raw_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
        bc_tmp = bc_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
        valid = ~np.isnan(station_tmp) & ~np.isnan(raw_tmp) & ~np.isnan(bc_tmp)
        if np.any(valid):
            station_q = np.nanquantile(station_tmp[valid], qs, method="hazen")
            raw_q = np.nanquantile(raw_tmp[valid], qs, method="hazen")
            bc_q = np.nanquantile(bc_tmp[valid], qs, method="hazen")
            raw_mae[i_station] = np.nanmean(np.abs(raw_q - station_q))
            bc_mae[i_station] = np.nanmean(np.abs(bc_q - station_q))
    return raw_mae, bc_mae


def getstationmeans(
    station: pd.DataFrame, raw: pd.DataFrame, corrected: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Means of yearly values over coincident valid years."""
    valid = station.notna() & raw.notna() & corrected.notna()
    return tuple(table.where(valid).mean(axis=0).to_numpy() for table in (station, raw, corrected))


def getdomainsummary(
    grid_yearly: np.ndarray,
    years: np.ndarray,
    grid_y: np.ndarray | None = None,
    coordinate_system: str = "projected",
) -> tuple[float, float]:
    """Mean and slope of the yearly area-weighted spatial-average series."""
    if grid_y is None:
        grid_y = np.zeros(grid_yearly.shape[:2])
    series = spatialmean(grid_yearly, grid_y, coordinate_system)
    valid = np.isfinite(series)
    mean = float(np.mean(series[valid])) if valid.any() else np.nan
    slope = theilsenslope(years[valid], series[valid]) if valid.sum() >= 2 else np.nan
    return mean, slope


def diagnosticunits(cfg: BiasCorrectionConfig) -> tuple[str, str, str]:
    """Plain-text native, yearly and trend units shared by CSV exporters."""
    from .plotting import _format_units, _yearly_units, _trend_units

    def plain(units: str) -> str:
        return units.replace("$", "").replace("{", "").replace("}", "")

    return tuple(map(plain, (
        _format_units(cfg.clim_var_units), _yearly_units(cfg), _trend_units(cfg),
    )))


def diagnosticcsvtable(table: pd.DataFrame, cfg: BiasCorrectionConfig) -> pd.DataFrame:
    """Add plain-text units on export, leaving internal metric names stable."""
    native, yearly, trend = diagnosticunits(cfg)
    headings = {}
    for column in table.columns:
        if column in {"Variable", "Station", "Dataset"}:
            continue
        units = native if column == "MAE quantiles" else trend if any(word in column.lower() for word in ("trend", "slope")) else yearly
        headings[column] = f"{column} ({units})"
    return table.rename(columns=headings)


def makesummarytable(
    clim_var_name: str,
    station_trends: np.ndarray,
    raw_station_trends: np.ndarray,
    bc_station_trends: np.ndarray,
    raw_quantile_mae: np.ndarray,
    bc_quantile_mae: np.ndarray,
    raw_annual_mae: np.ndarray,
    bc_annual_mae: np.ndarray,
    station_means: np.ndarray,
    raw_station_means: np.ndarray,
    bc_station_means: np.ndarray,
) -> pd.DataFrame:
    rows = [
        _summaryrow(
            clim_var_name,
            "Raw",
            station_trends,
            raw_station_trends,
            raw_quantile_mae,
            raw_annual_mae,
            station_means,
            raw_station_means,
        ),
        _summaryrow(
            clim_var_name,
            "Bias-corrected",
            station_trends,
            bc_station_trends,
            bc_quantile_mae,
            bc_annual_mae,
            station_means,
            bc_station_means,
        ),
    ]
    return pd.DataFrame(rows)


def savediagnosticsummarytable(
    summary_table: pd.DataFrame,
    file_path_figures_tables: str | Path,
    clim_var_name: str,
) -> None:
    output_dir = Path(file_path_figures_tables) / "overview"
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_table.to_csv(output_dir / f"{clim_var_name}_diagnostics_summary.csv", index=False)


def _summaryrow(
    clim_var_name: str,
    dataset: str,
    station_trends: np.ndarray,
    model_trends: np.ndarray,
    quantile_mae: np.ndarray,
    annual_mae: np.ndarray,
    station_means: np.ndarray,
    model_means: np.ndarray,
) -> dict[str, float | str]:
    return {
        "Variable": clim_var_name,
        "Dataset": dataset,
        "MAE quantiles": np.nanmean(quantile_mae),
        "MAE yearly": np.nanmean(annual_mae),
        "MAE trends": np.nanmean(np.abs(model_trends - station_trends)),
        "Observed mean": pd.Series(station_means).mean(),
        "Model mean": pd.Series(model_means).mean(),
        "Observed trend": pd.Series(station_trends).mean(),
        "Model trend": pd.Series(model_trends).mean(),
    }


def getoverlappingstationdata(
    station_clim_var: pd.DataFrame,
    raw_station_clim_var: pd.DataFrame,
    bc_station_clim_var: pd.DataFrame,
    station_time: pd.DatetimeIndex,
    grid_time: pd.DatetimeIndex,
    i_station: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not station_time.equals(grid_time):
        raise ValueError("Station and grid time vectors must match exactly.")
    raw_overlap = raw_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    bc_overlap = bc_station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    station_overlap = station_clim_var.iloc[:, i_station].to_numpy(dtype=float)
    valid = ~np.isnan(raw_overlap) & ~np.isnan(bc_overlap) & ~np.isnan(station_overlap)
    return station_overlap[valid], raw_overlap[valid], bc_overlap[valid]
