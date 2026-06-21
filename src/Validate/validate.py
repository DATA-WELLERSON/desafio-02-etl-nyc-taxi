"""Passo 3 — Validação de dados do NYC Yellow Taxi.

Estratégia: cada regra de anomalia vira uma Series booleana onde ``True`` marca a
linha que REPROVOU. Todas as regras são combinadas numa **única máscara OR**
(``invalid``) — basta reprovar em uma regra para ser descartada. No fim, mantemos
só ``df[~invalid]`` e devolvemos um relatório com o quality score do lote.

Retorno: ``(df_valido, relatorio_qualidade)``.
"""

from __future__ import annotations

import pandas as pd

from src import config


# Colunas que a validação precisa para aplicar todas as regras.
REQUIRED_COLUMNS = {
    config.PICKUP_DATETIME,
    config.DROPOFF_DATETIME,
    config.PICKUP_LON,
    config.PICKUP_LAT,
    config.DROPOFF_LON,
    config.DROPOFF_LAT,
    "trip_distance",
    "passenger_count",
    "fare_amount",
    "VendorID",
    "payment_type",
    "RatecodeID",
    "total_amount",
    *config.FARE_COMPONENTS,
}


def _outside_bbox(lon: pd.Series, lat: pd.Series) -> pd.Series:
    """``True`` onde a coordenada cai fora do bounding box de NYC (nulo também reprova)."""
    return (
        lon.isna()
        | lat.isna()
        | (lon < config.NYC_LON_MIN)
        | (lon > config.NYC_LON_MAX)
        | (lat < config.NYC_LAT_MIN)
        | (lat > config.NYC_LAT_MAX)
    )


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Valida o DataFrame bruto e retorna os válidos + relatório de qualidade."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no DataFrame: {sorted(missing)}")

    df = df.copy()
    rows_in = len(df)

    # 1) Datas -> datetime. Valores impossíveis viram NaT (não quebram o pipeline).
    df[config.PICKUP_DATETIME] = pd.to_datetime(df[config.PICKUP_DATETIME], errors="coerce")
    df[config.DROPOFF_DATETIME] = pd.to_datetime(df[config.DROPOFF_DATETIME], errors="coerce")

    # Auxiliares derivados das datas (usados em regras de duração e velocidade).
    duration_min = (
        df[config.DROPOFF_DATETIME] - df[config.PICKUP_DATETIME]
    ).dt.total_seconds() / 60.0

    # Velocidade média (mph), protegendo a divisão por zero (duração 0 -> NaN).
    hours = (duration_min / 60.0).replace(0, pd.NA)
    speed_mph = df["trip_distance"] / hours

    # 2) Relatório de nulos por coluna (só as que têm algum nulo).
    nulls = df.isna().sum()
    nulls_by_col = {col: int(n) for col, n in nulls.items() if n > 0}

    # 3) Regras de anomalia — cada máscara é True onde a linha REPROVA.
    rules: dict[str, pd.Series] = {}

    # --- Obrigatórias ---
    rules["data_invalida"] = (
        df[config.PICKUP_DATETIME].isna() | df[config.DROPOFF_DATETIME].isna()
    )
    rules["distancia"] = (
        df["trip_distance"].isna()
        | (df["trip_distance"] <= config.MIN_TRIP_DISTANCE)
        | (df["trip_distance"] > config.MAX_TRIP_DISTANCE)
    )
    rules["passageiros"] = (
        df["passenger_count"].isna()
        | (df["passenger_count"] < config.MIN_PASSENGERS)
        | (df["passenger_count"] > config.MAX_PASSENGERS)
    )
    rules["tarifa"] = (
        df["fare_amount"].isna()
        | (df["fare_amount"] <= config.MIN_FARE)
        | (df["fare_amount"] > config.MAX_FARE)
    )
    rules["duracao"] = (duration_min < config.MIN_DURATION_MIN) | (
        duration_min > config.MAX_DURATION_MIN
    )
    rules["coord_pickup"] = _outside_bbox(df[config.PICKUP_LON], df[config.PICKUP_LAT])
    rules["coord_dropoff"] = _outside_bbox(df[config.DROPOFF_LON], df[config.DROPOFF_LAT])

    # --- Opcionais ---
    rules["velocidade"] = speed_mph > config.MAX_SPEED_MPH
    rules["vendor"] = ~df["VendorID"].isin(config.VALID_VENDOR_IDS)
    rules["pagamento"] = ~df["payment_type"].isin(config.VALID_PAYMENT_TYPES)
    rules["ratecode"] = ~df["RatecodeID"].isin(config.VALID_RATECODE_IDS)

    # Consistência financeira: total_amount ~= soma dos componentes (com tolerância).
    componentes = df[config.FARE_COMPONENTS].sum(axis=1)
    rules["financeiro"] = (df["total_amount"] - componentes).abs() > config.FINANCIAL_TOLERANCE

    # Duplicados: mantém a 1ª ocorrência, marca as repetidas como reprovadas.
    subset_dup = [
        config.PICKUP_DATETIME,
        config.DROPOFF_DATETIME,
        "VendorID",
        "trip_distance",
        "total_amount",
    ]
    rules["duplicado"] = df.duplicated(subset=subset_dup, keep="first")

    # Comparações com NaN viram NaN; tratamos como "não reprova" (nulos já contados à parte).
    rules = {name: mask.fillna(False).astype(bool) for name, mask in rules.items()}

    # 4) Máscara OR única — reprovou em qualquer regra => inválida.
    invalid = pd.Series(False, index=df.index)
    for mask in rules.values():
        invalid |= mask

    # 5) Mantém só os válidos.
    df_valid = df[~invalid].copy()
    rows_out = len(df_valid)

    # 6) Quality score (0–100) = % de linhas aprovadas no lote.
    quality_score = round(100 * rows_out / rows_in, 2) if rows_in else 0.0

    report = {
        "rows_in": rows_in,
        "rows_out": rows_out,
        "rows_removed": rows_in - rows_out,
        "quality_score": quality_score,
        "nulls_by_column": nulls_by_col,
        "failures_by_rule": {name: int(mask.sum()) for name, mask in rules.items()},
        "failure_pct_by_rule": {
            name: (round(100 * int(mask.sum()) / rows_in, 2) if rows_in else 0.0)
            for name, mask in rules.items()
        },
    }

    return df_valid, report
