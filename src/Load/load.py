"""Passo 6 — Persistência: grava o DataFrame tratado em Parquet (engine pyarrow)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import config


def load(df: pd.DataFrame, output_path: Path = config.TRIPS_PARQUET) -> Path:
    """Salva o DataFrame em Parquet, criando o diretório de saída se necessário.

    Args:
        df: DataFrame tratado e enriquecido (nível de corrida).
        output_path: caminho do arquivo ``.parquet`` de saída.

    Returns:
        O caminho do arquivo gravado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, engine="pyarrow", index=False)
    return output_path
