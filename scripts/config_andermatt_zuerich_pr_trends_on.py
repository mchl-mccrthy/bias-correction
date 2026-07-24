from pathlib import Path

from eqtm import BiasCorrectionConfig


def config_andermatt_zuerich_pr_trends_on() -> BiasCorrectionConfig:
    repo_root = Path(__file__).resolve().parents[1]

    return BiasCorrectionConfig(
        clim_var_name="pr",
        clim_var_long_name="Precipitation",
        clim_var_units="mm",
        qmf_period="monthly",
        bc_type="multiplicative",
        trend_method="station",
        trend_window=365 * 5,
        agg_method="sum",
        write_output=True,
        n_quantiles=1001,
        idw_power=2,
        idw_method="elevation_aware",
        idw_alpha=10,
        multiplicative_epsilon=0.1,
        use_parallel=False,
        n_workers=None,
        keep_grid_biases=False,
        coordinate_system="geographic",
        file_path_station_coords=repo_root / "input_data" / "andermatt_zuerich_1981_2019" / "station" / "andermatt_zuerich_coordinates.csv",
        file_path_station_clim_var=repo_root / "input_data" / "andermatt_zuerich_1981_2019" / "station" / "andermatt_zuerich_pr.csv",
        file_path_raw_data=repo_root / "input_data" / "andermatt_zuerich_1981_2019" / "gridded" / "pr_andermatt_zuerich_1981_2019.nc",
        file_path_bc_data=repo_root / "output_data" / "andermatt_zuerich_1981_2019" / "trends_on" / "gridded" / "pr_bc_andermatt_zuerich_1981_2019.nc",
        file_path_figures=repo_root / "output_data" / "andermatt_zuerich_1981_2019" / "trends_on" / "figures",
    )
