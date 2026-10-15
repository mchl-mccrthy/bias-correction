"""Generate figures and the in-sample table from existing bias-corrected outputs."""

from paper.scripts.make_annual_mae_plots import main as make_annual_mae_plots
from paper.scripts.make_diagnostics_table import main as make_diagnostics_table
from paper.scripts.make_elevation_plots import main as make_elevation_plots
from paper.scripts.make_maps import main as make_maps
from paper.scripts.make_quantile_residual_plots import main as make_quantile_residual_plots
from paper.scripts.make_seasonal_trend_mae_plots import main as make_seasonal_trend_mae_plots
from paper.scripts.make_qq_plots import main as make_qq_plots
from paper.scripts.make_quantile_mae_plots import main as make_quantile_mae_plots
from paper.scripts.make_trend_ae_plots import main as make_trend_ae_plots
from paper.scripts.make_trend_scatter_plots import main as make_trend_scatter_plots


def main() -> None:
    make_maps()
    make_elevation_plots()
    make_qq_plots()
    make_quantile_residual_plots()
    make_annual_mae_plots()
    make_quantile_mae_plots()
    make_trend_ae_plots()
    make_trend_scatter_plots()
    make_seasonal_trend_mae_plots()
    make_diagnostics_table()


if __name__ == "__main__":
    main()
