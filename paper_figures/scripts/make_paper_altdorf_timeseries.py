from __future__ import annotations

from pathlib import Path

import numpy as np

from eqtm import makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics
from eqtm.plotting import _new_figure, _save_figure, _set_plot_style, _yearly_units
from paper_figures.scripts.make_paper_qq import ON_COLOR, RAW_COLOR
from scripts.config_andermatt_zuerich_pr_trends_on import config_andermatt_zuerich_pr_trends_on
from scripts.config_andermatt_zuerich_tas_trends_on import config_andermatt_zuerich_tas_trends_on


STATION_COLOR = "#009E73"
STATION_NAME = "Altdorf"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    figure_dir = repo_root / "paper_figures" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    _set_plot_style()

    _paper_timeseries(config_andermatt_zuerich_tas_trends_on(), figure_dir)
    _paper_timeseries(config_andermatt_zuerich_pr_trends_on(), figure_dir)


def _paper_timeseries(cfg: BiasCorrectionConfig, figure_dir: Path) -> None:
    diagnostics = makediagnostics(cfg)
    i_station = _station_index(diagnostics, STATION_NAME)

    fig, ax = _new_figure(6.5, 2, 4)
    units = _yearly_units(cfg)

    ax.plot(
        diagnostics.years,
        diagnostics.raw_station_clim_var_yearly.iloc[:, i_station],
        color=RAW_COLOR,
        label="Raw",
    )
    ax.plot(
        diagnostics.years,
        diagnostics.bc_station_clim_var_yearly.iloc[:, i_station],
        color=ON_COLOR,
        label="Bias-corrected",
    )
    ax.plot(
        diagnostics.years,
        diagnostics.station_clim_var_yearly.iloc[:, i_station],
        color=STATION_COLOR,
        label="Station",
    )

    ax.set_ylabel(f"{cfg.clim_var_long_name} ({units})")
    ax.set_xlim(np.min(diagnostics.years), np.max(diagnostics.years))
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)

    _save_figure(fig, figure_dir / f"{cfg.clim_var_name}_paper_{STATION_NAME.lower()}_yearly_timeseries.png")


def _station_index(diagnostics: Diagnostics, station_name: str) -> int:
    if "station" in diagnostics.station_coords:
        station_names = [str(value) for value in diagnostics.station_coords["station"]]
    else:
        station_names = [str(value) for value in diagnostics.station_clim_var.columns]

    try:
        return station_names.index(station_name)
    except ValueError as exc:
        raise ValueError(f"Station not found: {station_name}") from exc


if __name__ == "__main__":
    main()
