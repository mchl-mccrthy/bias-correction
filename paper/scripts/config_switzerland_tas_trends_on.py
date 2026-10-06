from pathlib import Path

from eqtm import BiasCorrectionConfig


def config_switzerland_tas_trends_on() -> BiasCorrectionConfig:
    repo_root = Path(__file__).resolve().parents[2]
    input_root = repo_root / "input_data" / "switzerland_1981_2020"
    output_root = repo_root / "output_data" / "switzerland_1981_2020" / "trends_on"

    return BiasCorrectionConfig(
        clim_var_name="tas",
        clim_var_long_name="Temperature",
        clim_var_units="degC",
        qmf_period="monthly",
        bc_type="additive",
        trend_mapping=True,
        trend_window=365 * 5,
        agg_method="mean",
        write_output=True,
        n_quantiles=1001,
        idw_power=1,
        idw_alpha=10,
        multiplicative_epsilon=0.1,
        use_parallel=True,
        n_workers=10,
        keep_grid_biases=False,
        coordinate_system="geographic",
        file_path_station_coords=input_root / "station" / "switzerland_coordinates.csv",
        file_path_station_clim_var=input_root / "station" / "switzerland_tas.csv",
        file_path_raw_data=input_root / "gridded" / "tas_switzerland_1981_2020.nc",
        file_path_bc_data=output_root / "gridded" / "tas_bc_switzerland_1981_2020.nc",
        file_path_figures_tables=output_root / "figures_and_tables",
    )
