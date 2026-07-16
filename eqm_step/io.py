from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class GridData:
    clim_var: np.ndarray
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray | None
    time: pd.DatetimeIndex
    dataset: xr.Dataset
    variable_dims: tuple[str, ...]


@dataclass
class StationData:
    clim_var: pd.DataFrame
    coords: pd.DataFrame
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray | None
    time: pd.DatetimeIndex


def hasncvar(file_path: str | Path, var_name: str) -> bool:
    with xr.open_dataset(file_path, decode_times=False) as ds:
        return var_name in ds.variables


def loadgriddata(file_path_grid_data: str | Path, clim_var_name: str) -> GridData:
    ds = xr.open_dataset(file_path_grid_data, decode_times=False)
    if clim_var_name not in ds:
        raise KeyError(f"Variable not found in grid file: {clim_var_name}")

    grid_x, grid_y, grid_z = loadgridcoords(ds)
    da = ds[clim_var_name]
    time_name = _find_time_name(ds)
    x_name, y_name = _find_xy_names(ds)

    if time_name not in da.dims:
        raise ValueError(f"{clim_var_name} must have a time dimension.")
    grid_clim_var = da.transpose(y_name, x_name, time_name).values
    grid_time = _decode_time(ds[time_name])

    return GridData(
        clim_var=grid_clim_var,
        x=grid_x,
        y=grid_y,
        z=grid_z,
        time=grid_time,
        dataset=ds,
        variable_dims=tuple(da.dims),
    )


def loadgridcoords(ds: xr.Dataset) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    x_name, y_name = _find_xy_names(ds)
    x = ds[x_name].values
    y = ds[y_name].values
    grid_x, grid_y = np.meshgrid(x, y)

    grid_z = None
    for z_name in ("z", "elevation", "elev", "orog"):
        if z_name in ds.variables:
            z_values = ds[z_name].values
            if z_values.ndim == 1:
                grid_z = np.tile(z_values.reshape(-1, 1), (1, grid_x.shape[1]))
            else:
                grid_z = _orient_grid(z_values, grid_x.shape)
            break

    return grid_x, grid_y, grid_z


def loadstationdata(
    file_path_station_clim_var: str | Path,
    file_path_station_coords: str | Path,
) -> StationData:
    station_clim_var = pd.read_csv(file_path_station_clim_var)
    station_coords = pd.read_csv(file_path_station_coords)
    station_x, station_y, station_z = loadstationcoords(station_coords)

    station_time = pd.to_datetime(
        {
            "year": station_clim_var["year"],
            "month": station_clim_var["month"],
            "day": station_clim_var["day"],
        }
    )
    station_clim_var = station_clim_var.drop(columns=["year", "month", "day"])

    if len(station_x) != station_clim_var.shape[1]:
        raise ValueError("Number of station coordinates must match number of station data columns.")

    return StationData(
        clim_var=station_clim_var,
        coords=station_coords,
        x=station_x,
        y=station_y,
        z=station_z,
        time=pd.DatetimeIndex(station_time),
    )


def loadstationcoords(station_coords: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    columns = set(station_coords.columns)
    if {"lon", "lat"}.issubset(columns):
        station_x = station_coords["lon"].to_numpy()
        station_y = station_coords["lat"].to_numpy()
    elif {"x", "y"}.issubset(columns):
        station_x = station_coords["x"].to_numpy()
        station_y = station_coords["y"].to_numpy()
    elif {"longitude", "latitude"}.issubset(columns):
        station_x = station_coords["longitude"].to_numpy()
        station_y = station_coords["latitude"].to_numpy()
    else:
        raise ValueError(
            "Station coordinate file must contain lon/lat, x/y, or longitude/latitude columns."
        )

    station_z = None
    for z_name in ("z", "elevation", "elev"):
        if z_name in columns:
            station_z = station_coords[z_name].to_numpy()
            break

    return station_x, station_y, station_z


def savebcdata(
    bc_clim_var: np.ndarray,
    file_path_raw_data: str | Path,
    file_path_bc_data: str | Path,
    clim_var_name: str,
) -> None:
    file_path_bc_data = Path(file_path_bc_data)
    shutil.copyfile(file_path_raw_data, file_path_bc_data)

    with xr.open_dataset(file_path_bc_data, decode_times=False) as ds_open:
        ds = ds_open.load()

    da = ds[clim_var_name]
    original_dims = da.dims
    original_attrs = da.attrs
    original_dtype = da.dtype
    bc_clim_var = bc_clim_var.astype(original_dtype, copy=False)

    x_name, y_name = _find_xy_names(ds)
    time_name = _find_time_name(ds)

    internal = xr.DataArray(
        bc_clim_var,
        coords={
            y_name: ds[y_name],
            x_name: ds[x_name],
            time_name: ds[time_name],
        },
        dims=(y_name, x_name, time_name),
        attrs=original_attrs,
    )

    ds[clim_var_name] = internal.transpose(*original_dims)

    ds[clim_var_name].attrs["bias_correction"] = "empirical quantile mapping"
    ds.attrs["history"] = f"replaced {clim_var_name} with bias-corrected data (EQM)"

    tmp_path = file_path_bc_data.with_suffix(file_path_bc_data.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    ds.to_netcdf(tmp_path)
    tmp_path.replace(file_path_bc_data)


def _find_xy_names(ds: xr.Dataset) -> tuple[str, str]:
    for x_name, y_name in (("lon", "lat"), ("x", "y"), ("longitude", "latitude")):
        if x_name in ds.variables and y_name in ds.variables:
            return x_name, y_name
    raise ValueError("Grid file must contain lon/lat, x/y, or longitude/latitude variables.")


def _find_time_name(ds: xr.Dataset) -> str:
    if "time" in ds.variables:
        return "time"
    raise ValueError("Grid file must contain a time variable.")


def _decode_time(time_da: xr.DataArray) -> pd.DatetimeIndex:
    units = time_da.attrs.get("units", "")
    match = re.match(r"^(?P<unit>\w+)\s+since\s+(?P<ref>.+)$", units)
    if match is None:
        raise ValueError(f"Unsupported NetCDF time units format: {units}")

    unit = match.group("unit").lower()
    ref = pd.Timestamp(match.group("ref").strip())
    values = time_da.values
    if unit in {"day", "days"}:
        offsets = pd.to_timedelta(values, unit="D")
    elif unit in {"hour", "hours"}:
        offsets = pd.to_timedelta(values, unit="h")
    elif unit in {"second", "seconds"}:
        offsets = pd.to_timedelta(values, unit="s")
    else:
        raise ValueError(f"Unsupported time unit: {unit}")
    return pd.DatetimeIndex(ref + offsets)


def _orient_grid(values: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
    if values.shape == target_shape:
        return values
    if values.T.shape == target_shape:
        return values.T
    raise ValueError(f"Grid variable shape {values.shape} does not match coordinates {target_shape}.")
