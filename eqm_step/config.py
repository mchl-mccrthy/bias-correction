from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class BiasCorrectionConfig:
    """Configuration for an EQM-STeP bias-correction workflow.

    The configuration stores variable metadata, quantile-mapping options,
    trend-preservation settings, IDW interpolation settings, and file paths
    used by `biascorrect`, `makediagnostics`, and `makeplots`.
    """

    clim_var_name: str
    clim_var_long_name: str
    clim_var_units: str
    qmf_period: str
    bc_type: str
    preserve_trends: bool
    trend_window: int
    agg_method: str
    write_output: bool
    n_quantiles: int
    idw_power: float
    idw_method: str
    idw_alpha: float
    use_parallel: bool
    n_workers: int | None
    multiplicative_epsilon: float
    keep_grid_biases: bool
    coordinate_system: str
    file_path_station_coords: str | Path
    file_path_station_clim_var: str | Path
    file_path_raw_data: str | Path
    file_path_bc_data: str | Path
    file_path_figures: str | Path


def validateconfig(cfg: BiasCorrectionConfig) -> None:
    """Validate user-facing configuration options and required input files."""

    _must_be_one_of(cfg.qmf_period, {"whole", "seasonal", "monthly"}, "qmf_period")
    _must_be_one_of(cfg.bc_type, {"additive", "multiplicative"}, "bc_type")
    _must_be_one_of(cfg.agg_method, {"mean", "sum"}, "agg_method")
    _must_be_one_of(cfg.coordinate_system, {"geographic", "projected"}, "coordinate_system")
    _must_be_one_of(cfg.idw_method, {"horizontal", "elevation_aware"}, "idw_method")

    if cfg.trend_window <= 0:
        raise ValueError("cfg.trend_window must be positive.")
    if cfg.n_quantiles <= 1:
        raise ValueError("cfg.n_quantiles must be greater than 1.")
    if cfg.idw_power <= 0:
        raise ValueError("cfg.idw_power must be positive.")
    if cfg.idw_alpha <= 0:
        raise ValueError("cfg.idw_alpha must be positive.")
    if cfg.multiplicative_epsilon < 0:
        raise ValueError("cfg.multiplicative_epsilon must be non-negative.")
    if cfg.n_workers is not None and cfg.n_workers <= 0:
        raise ValueError("cfg.n_workers must be None or a positive integer.")

    for field_name in (
        "file_path_station_coords",
        "file_path_station_clim_var",
        "file_path_raw_data",
    ):
        path = Path(getattr(cfg, field_name))
        if not path.is_file():
            raise FileNotFoundError(f"{field_name} not found: {path}")


def _must_be_one_of(value: str, allowed: set[str], field_name: str) -> None:
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"cfg.{field_name} must be one of: {allowed_text}")
