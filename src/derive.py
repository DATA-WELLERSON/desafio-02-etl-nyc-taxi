"""Cálculos derivados compartilhados entre as etapas do pipeline.

Centraliza fórmulas usadas em mais de um passo (Validate e Transform), evitando
lógica duplicada: duração da corrida, velocidade média e o padrão de divisão
"à prova de zero".
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divisão protegida: zero no denominador vira NaN e o resultado final vira 0."""
    return (numerator / denominator.replace(0, np.nan)).fillna(0.0)


def duration_minutes(pickup: pd.Series, dropoff: pd.Series) -> pd.Series:
    """Duração da corrida em minutos (dropoff − pickup)."""
    return (dropoff - pickup).dt.total_seconds() / 60.0


def speed_mph(distance: pd.Series, duration_min: pd.Series) -> pd.Series:
    """Velocidade média em milhas/hora, protegendo a divisão por zero."""
    hours = duration_min / 60.0
    return safe_divide(distance, hours)
