"""Passos 7 e 8 — Dashboard em Streamlit (base inicial).

Lê o Parquet gerado pelo ETL e exibe KPIs e os dados. As views por hora,
fornecedor, pagamento e dia da semana entram nos próximos passos.

Rode com:
    uv run streamlit run dashboard.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import config


@st.cache_data
def load_data(path: str = str(config.TRIPS_PARQUET)) -> pd.DataFrame:
    return pd.read_parquet(path)


st.set_page_config(page_title="NYC Yellow Taxi", layout="wide")
st.title("Dashboard — NYC Yellow Taxi")

try:
    df = load_data()
except FileNotFoundError:
    st.warning(
        "Parquet não encontrado. Rode o pipeline primeiro: `uv run python etl.py`."
    )
    st.stop()

st.metric("Total de corridas", f"{len(df):,}")
st.dataframe(df.head(1000))
