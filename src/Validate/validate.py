"""Passo 3 — Validação de dados (STUB).

A implementação completa entra no próximo passo: conversão de datas, regras de
anomalia combinadas em máscara OR única, filtro dos válidos e quality score.
"""

from __future__ import annotations

import pandas as pd


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Placeholder: retorna o DataFrame inalterado e um relatório vazio.

    Returns:
        (df_valido, relatorio_qualidade)
    """
    report: dict = {"status": "not_implemented", "rows_in": len(df), "rows_out": len(df)}
    return df, report
