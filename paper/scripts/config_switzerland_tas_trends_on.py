from eqtm import BiasCorrectionConfig


def config_switzerland_tas_trends_on() -> BiasCorrectionConfig:
    return BiasCorrectionConfig(
        clim_var_name="tas",
        clim_var_long_name="Mean temperature",
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
        file_path_station_coords="/storage/mccarthy/climate_pipeline/data/Switzerland/interim/stations/switzerland_coordinates.csv",
        file_path_station_clim_var="/storage/mccarthy/climate_pipeline/data/Switzerland/interim/stations/switzerland_tas.csv",
        file_path_raw_data="/storage/mccarthy/climate_pipeline/data/Switzerland/interim/chelsa/tas_switzerland_1981_2019.nc",
        file_path_bc_data="/storage/mccarthy/climate_pipeline/data/Switzerland/processed/key_variables/historic/reanalysis/trends_on/tas_bc_switzerland_1981_2019.nc",
        file_path_figures_tables="/storage/mccarthy/climate_pipeline/data/Switzerland/processed/key_variables/historic/reanalysis/trends_on/figures",
    )
