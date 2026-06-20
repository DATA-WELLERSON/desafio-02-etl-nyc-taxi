"""Passo 2 — Extração: leitura do CSV bruto do NYC Yellow Taxi para um DataFrame."""

from __future__ import annotations

import pandas as pd

from src import config


def extract(
    file_path: str = config.DEFAULT_CSV,
    dataset: str = config.KAGGLE_DATASET,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Carrega um CSV do dataset do Kaggle e retorna um DataFrame.

    Usa ``kagglehub`` com o adaptador do pandas. Requer credenciais Kaggle
    configuradas (``kaggle.json`` em ``%USERPROFILE%/.kaggle`` ou as variáveis
    de ambiente ``KAGGLE_USERNAME`` / ``KAGGLE_KEY``).

    Args:
        file_path: nome do arquivo CSV dentro do dataset (ex.: ``yellow_tripdata_2016-01.csv``).
        dataset: slug do dataset no Kaggle (``owner/dataset``).
        nrows: se informado, lê apenas as N primeiras linhas (útil em desenvolvimento,
            pois os arquivos têm ~2 GB).

    Returns:
        DataFrame com os dados brutos.
    """
    try:
        import kagglehub
        from kagglehub import KaggleDatasetAdapter
    except ImportError as exc:  # pragma: no cover - dependência opcional em dev
        raise ImportError(
            "kagglehub não está instalado. Rode `uv add kagglehub`."
        ) from exc

    pandas_kwargs = {"nrows": nrows} if nrows is not None else {}

    try:
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            dataset,
            file_path,
            pandas_kwargs=pandas_kwargs,
        )
    except Exception as exc:  # noqa: BLE001 - re-empacota com dica de credenciais
        raise RuntimeError(
            f"Falha ao baixar '{file_path}' de '{dataset}'. "
            "Verifique suas credenciais do Kaggle (kaggle.json ou "
            "KAGGLE_USERNAME/KAGGLE_KEY) e a conexão de rede."
        ) from exc

    return df


def read_csv(path: str, nrows: int | None = None) -> pd.DataFrame:
    """Lê um CSV local já baixado (alternativa ao download via kagglehub)."""
    return pd.read_csv(path, nrows=nrows)
