"""Leitura de um CSV local já baixado (alternativa ao download via kagglehub)."""

from __future__ import annotations

import pandas as pd


def read_csv(path: str, nrows: int | None = None) -> pd.DataFrame:
    """Lê um CSV local já baixado (alternativa ao download via kagglehub)."""
    return pd.read_csv(path, nrows=nrows)
