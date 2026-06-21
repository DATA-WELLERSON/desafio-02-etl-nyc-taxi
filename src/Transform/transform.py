"""Passo 4 — Transformações e criação de novas colunas do NYC Yellow Taxi.

Recebe o DataFrame já validado (datas convertidas, sem anomalias) e o enriquece
com colunas derivadas: temporais (data/hora/turno/dia da semana), métricas
(duração, velocidade, % de gorjeta), faixas (distância/duração), rentabilidade e
uma flag de anomalia combinada.

Divisões usam o padrão "à prova de zero": ``replace(0, NaN)`` no denominador →
divide → ``fillna(0)``, evitando ``inf``/``NaN`` que quebrariam as agregações.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divisão protegida: zero no denominador vira NaN e o resultado final vira 0."""
    return (numerator / denominator.replace(0, np.nan)).fillna(0.0)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece o DataFrame validado com colunas derivadas."""
    df = df.copy()

    pickup = df[config.PICKUP_DATETIME]
    dropoff = df[config.DROPOFF_DATETIME]

    # Validate já converte para datetime; reconverte se vier de uso isolado.
    if not pd.api.types.is_datetime64_any_dtype(pickup):
        pickup = pd.to_datetime(pickup, errors="coerce")
        dropoff = pd.to_datetime(dropoff, errors="coerce")

    # --- Padronização temporal ---
    df["pickup_date"] = pickup.dt.strftime("%Y-%m-%d")  # texto, Parquet-friendly
    df["pickup_hour"] = pickup.dt.hour
    df["weekday"] = pickup.dt.weekday  # 0=segunda ... 6=domingo
    df["weekday_name"] = df["weekday"].map(dict(enumerate(config.WEEKDAY_NAMES)))
    df["is_weekend"] = df["weekday"] >= 5

    # Turno do dia a partir da hora (bins derivados de config.SHIFTS).
    shift_edges = [s[0] for s in config.SHIFTS] + [config.SHIFTS[-1][1]]
    df["shift"] = pd.cut(
        df["pickup_hour"],
        bins=shift_edges,
        right=False,
        labels=[s[2] for s in config.SHIFTS],
    )

    # --- Métricas derivadas ---
    duration_min = (dropoff - pickup).dt.total_seconds() / 60.0
    df["duration_min"] = duration_min.round(2)

    hours = duration_min / 60.0
    df["speed_mph"] = _safe_divide(df["trip_distance"], hours).round(2)
    df["tip_pct"] = _safe_divide(df["tip_amount"], df["fare_amount"]).mul(100).round(2)

    # --- Rentabilidade ---
    df["revenue_per_min"] = _safe_divide(df["total_amount"], duration_min).round(2)
    df["revenue_per_mile"] = _safe_divide(df["total_amount"], df["trip_distance"]).round(2)

    # --- Faixas (categóricas) ---
    df["distance_band"] = pd.cut(
        df["trip_distance"],
        bins=config.DISTANCE_BAND_BINS,
        labels=config.DISTANCE_BAND_LABELS,
        include_lowest=True,
    )
    df["duration_band"] = pd.cut(
        df["duration_min"],
        bins=config.DURATION_BAND_BINS,
        labels=config.DURATION_BAND_LABELS,
        include_lowest=True,
    )

    # --- Flag de anomalia combinada: velocidade alta E tarifa baixa ---
    df["anomaly_flag"] = (df["speed_mph"] > config.ANOMALY_SPEED_MPH) & (
        df["fare_amount"] < config.ANOMALY_FARE
    )

    return df
