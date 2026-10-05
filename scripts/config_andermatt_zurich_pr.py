from pathlib import Path

from eqtm import BiasCorrectionConfig


def config_andermatt_zurich_pr() -> BiasCorrectionConfig:
    repo_root = Path(__file__).resolve().parents[1]

    return BiasCorrectionConfig(
        clim_var_name="pr",
        clim_var_long_name="Precipitation",
        clim_var_units="mm day^{-1}",
        qmf_period="monthly",
        bc_type="multiplicative",
        trend_mapping=True,
        trend_window=365 * 5,
        agg_method="sum",
        write_output=True,
        n_quantiles=1001,
        idw_power=1,
        idw_alpha=10,
        multiplicative_epsilon=0.1,
        use_parallel=False,
        n_workers=None,
        keep_grid_biases=False,
        coordinate_system="geographic",
        file_path_station_coords=repo_root / "input_data" / "andermatt_zurich_1981_2020" / "station" / "andermatt_zurich_coordinates.csv",
        file_path_station_clim_var=repo_root / "input_data" / "andermatt_zurich_1981_2020" / "station" / "andermatt_zurich_pr.csv",
        file_path_raw_data=repo_root / "input_data" / "andermatt_zurich_1981_2020" / "gridded" / "pr_andermatt_zurich_1981_2020.nc",
        file_path_bc_data=repo_root / "output_data" / "andermatt_zurich_1981_2020" / "gridded" / "pr_bc_andermatt_zurich_1981_2020.nc",
        file_path_figures_tables=repo_root / "output_data" / "andermatt_zurich_1981_2020" / "figures_and_tables",
    )
