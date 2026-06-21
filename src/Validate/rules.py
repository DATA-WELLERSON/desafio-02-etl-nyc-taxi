"""Regras de anomalia auxiliares usadas pela validação (Passo 3)."""

from __future__ import annotations

import pandas as pd

from src import config


def outside_bbox(lon: pd.Series, lat: pd.Series) -> pd.Series:
    """``True`` onde a coordenada cai fora do bounding box de NYC (nulo também reprova)."""
    return (
        lon.isna()
        | lat.isna()
        | (lon < config.NYC_LON_MIN)
        | (lon > config.NYC_LON_MAX)
        | (lat < config.NYC_LAT_MIN)
        | (lat > config.NYC_LAT_MAX)
    )
