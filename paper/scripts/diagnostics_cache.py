from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from typing import Any

from eqtm import makediagnostics as _makediagnostics
from eqtm.config import BiasCorrectionConfig
from eqtm.diagnostics import Diagnostics


_CACHE: dict[tuple[Any, ...], Diagnostics] = {}


def makediagnostics_cached(cfg: BiasCorrectionConfig) -> Diagnostics:
    """Return cached diagnostics for repeated paper plotting calls."""

    key = _config_key(cfg)
    if key not in _CACHE:
        print(f"Computing diagnostics: {cfg.clim_var_name}, trend_mapping={cfg.trend_mapping}", flush=True)
        _CACHE[key] = _makediagnostics(cfg)
    return _CACHE[key]


def _config_key(cfg: BiasCorrectionConfig) -> tuple[Any, ...]:
    values = []
    for field in fields(cfg):
        value = getattr(cfg, field.name)
        if isinstance(value, Path):
            value = str(value)
        values.append((field.name, value))
    return tuple(values)
