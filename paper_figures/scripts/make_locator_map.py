from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import xarray as xr

from eqm_step.plotting import BOX_LINE_WIDTH, CM_TO_IN, FONT_SIZE, _set_plot_style
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    boundary_path = _find_boundary_file(repo_root / "input_data" / "boundaries")
    figure_dir = repo_root / "paper_figures" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    switzerland = _load_switzerland_boundary(boundary_path)
    study_extent = _study_area_extent(config_andermatt_zuerich_tas_trends_on().file_path_raw_data)
    _locator_map(switzerland, study_extent, figure_dir / "switzerland_locator_map.png")


def _find_boundary_file(boundary_dir: Path) -> Path:
    preferred = boundary_dir / "switzerland_boundary.geojson"
    if preferred.is_file():
        return preferred

    candidates = sorted(boundary_dir.rglob("*.shp"))
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        "No boundary file found. Expected input_data/boundaries/switzerland_boundary.geojson "
        "or a Natural Earth shapefile under input_data/boundaries/."
    )


def _load_switzerland_boundary(boundary_path: Path) -> gpd.GeoDataFrame:
    boundaries = gpd.read_file(boundary_path)
    if boundaries.crs is None:
        boundaries = boundaries.set_crs("EPSG:4326")
    boundaries = boundaries.to_crs("EPSG:4326")

    for column in ("ADMIN", "NAME", "NAME_EN", "SOVEREIGNT"):
        if column in boundaries.columns:
            match = boundaries[column].astype(str).str.lower() == "switzerland"
            if match.any():
                return boundaries.loc[match]

    return boundaries


def _study_area_extent(file_path_raw_data: str | Path) -> tuple[float, float, float, float]:
    with xr.open_dataset(file_path_raw_data, decode_times=False) as ds:
        x_name, y_name = _find_xy_names(ds)
        x = ds[x_name].values
        y = ds[y_name].values

    return float(np.nanmin(x)), float(np.nanmax(x)), float(np.nanmin(y)), float(np.nanmax(y))


def _find_xy_names(ds: xr.Dataset) -> tuple[str, str]:
    for x_name, y_name in (("lon", "lat"), ("x", "y"), ("longitude", "latitude")):
        if x_name in ds.variables and y_name in ds.variables:
            return x_name, y_name
    raise ValueError("Grid file must contain lon/lat, x/y, or longitude/latitude variables.")


def _locator_map(
    switzerland: gpd.GeoDataFrame,
    study_extent: tuple[float, float, float, float],
    path: Path,
) -> None:
    min_x, min_y, max_x, max_y = switzerland.total_bounds
    x_pad = 0.08 * (max_x - min_x)
    y_pad = 0.08 * (max_y - min_y)
    x_lims = (min_x - x_pad, max_x + x_pad)
    y_lims = (min_y - y_pad, max_y + y_pad)

    mean_lat = 0.5 * (y_lims[0] + y_lims[1])
    lon_scale = np.cos(np.deg2rad(mean_lat))
    plot_width_cm = 3
    plot_height_cm = plot_width_cm * (y_lims[1] - y_lims[0]) / ((x_lims[1] - x_lims[0]) * lon_scale)
    margin_cm = 2

    fig_width_cm = margin_cm + plot_width_cm + margin_cm
    fig_height_cm = margin_cm + plot_height_cm + margin_cm
    fig, ax = plt.subplots(figsize=(fig_width_cm * CM_TO_IN, fig_height_cm * CM_TO_IN))

    left = margin_cm / fig_width_cm
    bottom = margin_cm / fig_height_cm
    width = plot_width_cm / fig_width_cm
    height = plot_height_cm / fig_height_cm
    ax.set_position([left, bottom, width, height])

    switzerland.boundary.plot(ax=ax, color="black", linewidth=BOX_LINE_WIDTH)

    x_min, x_max, y_min, y_max = study_extent
    rectangle = mpatches.Rectangle(
        (x_min, y_min),
        x_max - x_min,
        y_max - y_min,
        fill=False,
        edgecolor="red",
        linewidth=1,
    )
    ax.add_patch(rectangle)

    ax.set_xlim(x_lims)
    ax.set_ylim(y_lims)
    ax.set_aspect(1 / lon_scale, adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
