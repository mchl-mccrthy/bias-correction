from eqm_step import BiasCorrectionConfig


def config_andermatt_zuerich_tas() -> BiasCorrectionConfig:
    return BiasCorrectionConfig(
        clim_var_name="tas",
        clim_var_long_name="Temperature",
        clim_var_units="degC",
        qmf_period="monthly",
        bc_type="additive",
        preserve_trends=True,
        trend_window=365 * 5,
        agg_method="mean",
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
        file_path_station_coords=r"N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\input_data\meteoswiss\processed\andermatt_zuerich_coordinates.csv",
        file_path_station_clim_var=r"N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\input_data\meteoswiss\processed\andermatt_zuerich_tas.csv",
        file_path_raw_data=r"N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\input_data\chelsa\processed\andermatt_zuerich_1981_2019\tas_andermatt_zuerich_1981_2019.nc",
        file_path_bc_data=r"N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\output_data\andermatt_zuerich_1981_2019\tas_bc_andermatt_zuerich_1981_2019.nc",
        file_path_figures=r"N:\gebhyd\8_Him\Personal_folders\Mike\foracca\paper\output_data\figures",
    )
