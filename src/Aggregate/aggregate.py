"""Passo 5 — Agregações e métricas (STUB).

A implementação completa entra no próximo passo: métricas base (total_trips,
avg_distance, avg_fare, ...) e agregações por dia/semana/turno/vendor/rota.
"""

from __future__ import annotations

import pandas as pd


def base_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder: retorna uma única linha com a contagem de corridas."""
    return pd.DataFrame({"total_trips": [len(df)]})
