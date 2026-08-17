from pathlib import Path

from eqtm import BiasCorrectionConfig


def config_switzerland_tas_trends_off() -> BiasCorrectionConfig:
    repo_root = Path(__file__).resolve().parents[2]

    return BiasCorrectionConfig(
        clim_var_name="tas",
        clim_var_long_name="Temperature",
        clim_var_units="degC",
        qmf_period="monthly",
        bc_type="additive",
        trend_method="none",
        trend_window=365 * 5,
        agg_method="mean",
        write_output=True,
        n_quantiles=201,
        idw_power=1,
        idw_alpha=10,
        multiplicative_epsilon=0.1,
        use_parallel=False,
        n_workers=None,
        keep_grid_biases=False,
        coordinate_system="geographic",
        file_path_station_coords=repo_root / "input_data" / "switzerland_1981_2019" / "station" / "switzerland_coordinates.csv",
        file_path_station_clim_var=repo_root / "input_data" / "switzerland_1981_2019" / "station" / "switzerland_tas.csv",
        file_path_raw_data=repo_root / "input_data" / "switzerland_1981_2019" / "gridded" / "tas_switzerland_1981_2019.nc",
        file_path_bc_data=repo_root / "output_data" / "switzerland_1981_2019" / "trends_off" / "gridded" / "tas_bc_switzerland_1981_2019.nc",
        file_path_figures_tables=repo_root / "output_data" / "switzerland_1981_2019" / "trends_off" / "figures_and_tables",
    )
