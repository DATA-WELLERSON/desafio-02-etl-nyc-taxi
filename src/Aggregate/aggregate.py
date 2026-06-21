"""Passo 5 — Agregações e métricas do NYC Yellow Taxi.

Cada função recebe o DataFrame já transformado (nível de corrida) e devolve um
DataFrame agregado pronto para visualização. O mesmo conjunto de métricas base é
reutilizado por todos os recortes via ``_aggregate``, e o ``dashboard.py`` (Passo
8) consome estas funções para montar as views — evitando duplicar lógica.
"""

from __future__ import annotations

import pandas as pd

from src import config

# Fonte única das métricas base: nome -> (coluna, função de agregação).
NAMED_AGG = {
    "total_trips": ("trip_distance", "size"),
    "avg_distance": ("trip_distance", "mean"),
    "avg_fare": ("fare_amount", "mean"),
    "avg_duration": ("duration_min", "mean"),
    "avg_speed": ("speed_mph", "mean"),
    "avg_tip_pct": ("tip_pct", "mean"),
    "total_revenue": ("total_amount", "sum"),
}


def _finalize(agg: pd.DataFrame) -> pd.DataFrame:
    """Adiciona pct_trips (participação %) e arredonda as colunas numéricas."""
    total = int(agg["total_trips"].sum())
    agg["pct_trips"] = (agg["total_trips"] / total * 100) if total else 0.0
    num_cols = agg.select_dtypes("number").columns
    agg[num_cols] = agg[num_cols].round(2)
    return agg


def _aggregate(df: pd.DataFrame, by) -> pd.DataFrame:
    """Agrega as métricas base por uma ou mais colunas (``by``)."""
    grouped = df.groupby(by, observed=True).agg(
        **{name: pd.NamedAgg(col, func) for name, (col, func) in NAMED_AGG.items()}
    )
    return _finalize(grouped).reset_index()


def base_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Métricas globais do lote, em uma única linha (KPIs do dashboard)."""
    row = {
        name: (len(df) if func == "size" else getattr(df[col], func)())
        for name, (col, func) in NAMED_AGG.items()
    }
    return pd.DataFrame([row]).round(2)


def by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Agregação por dia (corridas, receita, ticket médio, gorjeta...)."""
    return _aggregate(df, "pickup_date").sort_values("pickup_date", ignore_index=True)


def by_week(df: pd.DataFrame) -> pd.DataFrame:
    """Agregação por semana (tendência/variação ao longo do tempo)."""
    df = df.copy()
    df["pickup_week"] = pd.to_datetime(df["pickup_date"]).dt.to_period("W").astype(str)
    return _aggregate(df, "pickup_week").sort_values("pickup_week", ignore_index=True)


def by_shift_payment(df: pd.DataFrame) -> pd.DataFrame:
    """Agregação por turno + tipo de pagamento."""
    return _aggregate(df, ["shift", "payment_type"])


def by_vendor_shift(df: pd.DataFrame) -> pd.DataFrame:
    """Agregação por fornecedor (VendorID) + turno."""
    return _aggregate(df, ["VendorID", "shift"])


def by_route(df: pd.DataFrame, top_n: int | None = 20) -> pd.DataFrame:
    """Rotas origem→destino de maior volume (coordenadas arredondadas em zonas)."""
    df = df.copy()
    d = config.ROUTE_COORD_DECIMALS
    df["origin"] = (
        df[config.PICKUP_LAT].round(d).astype(str)
        + ", "
        + df[config.PICKUP_LON].round(d).astype(str)
    )
    df["destination"] = (
        df[config.DROPOFF_LAT].round(d).astype(str)
        + ", "
        + df[config.DROPOFF_LON].round(d).astype(str)
    )
    routes = _aggregate(df, ["origin", "destination"]).sort_values(
        "total_trips", ascending=False, ignore_index=True
    )
    return routes.head(top_n) if top_n else routes


def percentiles(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    """Percentis (P50/P90/P95) de duração, distância e tarifa."""
    cols = cols or ["duration_min", "trip_distance", "fare_amount"]
    pcts = config.PERCENTILES
    out = df[cols].quantile(pcts)
    out.index = [f"p{int(p * 100)}" for p in pcts]
    return out.round(2).reset_index(names="percentile")


def quality_by_rule(report: dict) -> pd.DataFrame:
    """Tabela de qualidade por regra a partir do relatório do Validate (Passo 3)."""
    fails_pct = report.get("failure_pct_by_rule", {})
    fails_count = report.get("failures_by_rule", {})
    out = pd.DataFrame(
        {
            "rule": list(fails_pct.keys()),
            "failures": [fails_count.get(r, 0) for r in fails_pct],
            "failure_pct": list(fails_pct.values()),
        }
    )
    return out.sort_values("failure_pct", ascending=False, ignore_index=True)
