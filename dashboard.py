"""Passos 7 e 8 — Dashboard em Streamlit (NYC Yellow Taxi).

Lê o Parquet gerado pelo ETL, aplica filtros de sidebar e exibe:
  - KPIs globais (base_metrics)
  - Gráficos de visão geral: corridas por hora e receita por dia
  - Tabela exploratória
  - Esqueleto de tabs para as 4 views do Passo 8

Rode com:
    uv run streamlit run dashboard.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import config
from src.Aggregate import base_metrics, by_day

# ----------------------------------------------------------------------------- #
# Configuração da página
# ----------------------------------------------------------------------------- #
st.set_page_config(
    page_title="NYC Yellow Taxi",
    page_icon=":taxi:",
    layout="wide",
)

# ----------------------------------------------------------------------------- #
# Carregamento com cache — reutiliza o Parquet enquanto o arquivo não mudar
# ----------------------------------------------------------------------------- #

@st.cache_data
def load_data(path: str = str(config.TRIPS_PARQUET)) -> pd.DataFrame:
    """Lê o Parquet de corridas e retorna o DataFrame bruto."""
    return pd.read_parquet(path)


try:
    df_raw = load_data()
except FileNotFoundError:
    st.warning(
        "Parquet não encontrado. Rode o pipeline primeiro: `uv run python etl.py`."
    )
    st.stop()

# ----------------------------------------------------------------------------- #
# Sidebar — filtros opcionais (refiltram o df antes de tudo mais)
# ----------------------------------------------------------------------------- #
st.sidebar.title("Filtros")

# --- Turno ---
turnos_disponiveis = sorted(df_raw["shift"].dropna().unique().tolist())
turnos_selecionados = st.sidebar.multiselect(
    "Turno",
    options=turnos_disponiveis,
    default=turnos_disponiveis,
    help="madrugada | manha | tarde | noite",
)

# --- Fornecedor (VendorID) ---
vendors_disponiveis = sorted(df_raw["VendorID"].dropna().unique().tolist())
vendors_selecionados = st.sidebar.multiselect(
    "Fornecedor (VendorID)",
    options=vendors_disponiveis,
    default=vendors_disponiveis,
    help="1 = Creative Mobile Technologies, 2 = VeriFone",
)

# --- Dia da semana ---
# Mostra os nomes mas filtra pelo índice numérico (0=segunda...6=domingo)
WEEKDAY_MAP = {nome: idx for idx, nome in enumerate(config.WEEKDAY_NAMES)}
dias_disponiveis = list(config.WEEKDAY_NAMES)
dias_selecionados = st.sidebar.multiselect(
    "Dia da semana",
    options=dias_disponiveis,
    default=dias_disponiveis,
)
indices_dias = [WEEKDAY_MAP[d] for d in dias_selecionados]

# Aplica filtros ao df
df = df_raw[
    df_raw["shift"].isin(turnos_selecionados)
    & df_raw["VendorID"].isin(vendors_selecionados)
    & df_raw["weekday"].isin(indices_dias)
].copy()

# Avisa se o filtro zerou os dados
if df.empty:
    st.warning("Nenhuma corrida para os filtros selecionados. Ajuste os filtros na sidebar.")
    st.stop()

# ----------------------------------------------------------------------------- #
# Cabeçalho e contagem filtrada
# ----------------------------------------------------------------------------- #
st.title("Dashboard — NYC Yellow Taxi")
st.caption(
    f"Exibindo {len(df):,} corridas"
    f" ({len(df) / len(df_raw) * 100:.1f}% do total de {len(df_raw):,})"
)

# ----------------------------------------------------------------------------- #
# KPIs — consome base_metrics(df) sem duplicar lógica de agregação
# ----------------------------------------------------------------------------- #
kpis = base_metrics(df).iloc[0]

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric(
    "Total de corridas",
    f"{int(kpis['total_trips']):,}",
)
col2.metric(
    "Receita total (USD)",
    f"${kpis['total_revenue']:,.0f}",
)
col3.metric(
    "Ticket medio (USD)",
    f"${kpis['avg_fare']:.2f}",
)
col4.metric(
    "Distancia media (mi)",
    f"{kpis['avg_distance']:.2f}",
)
col5.metric(
    "Duracao media (min)",
    f"{kpis['avg_duration']:.1f}",
)
col6.metric(
    "Velocidade media (mph)",
    f"{kpis['avg_speed']:.1f}",
)
col7.metric(
    "Gorjeta media (%)",
    f"{kpis['avg_tip_pct']:.1f}%",
)

st.divider()

# ----------------------------------------------------------------------------- #
# Tabs — Passo 7: visao geral | Passo 8: 4 views detalhadas (esqueleto)
# ----------------------------------------------------------------------------- #
tab_geral, tab_hora, tab_vendor, tab_pagamento, tab_semana = st.tabs(
    ["Visao Geral", "Por Hora", "Por Fornecedor", "Por Pagamento", "Por Dia da Semana"]
)

# ========================= TAB: VISAO GERAL (Passo 7) ========================= #
with tab_geral:
    st.subheader("Corridas por hora do dia")

    # Agrupa corridas por hora — simples, sem chamar funcao de Aggregate
    # (by_hour nao existe no modulo; aqui e so um groupby rapido para o grafico)
    corridas_por_hora = (
        df.groupby("pickup_hour", observed=True)["trip_distance"]
        .size()
        .rename("total_corridas")
        .reset_index()
        .set_index("pickup_hour")
    )
    st.bar_chart(corridas_por_hora, y="total_corridas", color="#f5c518")

    st.divider()

    st.subheader("Receita total por dia")

    # Reutiliza by_day() do Aggregate — sem duplicar logica
    df_dia = by_day(df).set_index("pickup_date")
    st.line_chart(df_dia["total_revenue"])

    st.divider()

    # Tabela exploratoria — limita linhas para nao travar o browser
    MAX_LINHAS_TABELA = 2_000
    st.subheader(f"Amostra dos dados (ate {MAX_LINHAS_TABELA:,} linhas)")

    COLUNAS_TABELA = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "VendorID",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "tip_amount",
        "total_amount",
        "payment_type",
        "shift",
        "duration_min",
        "speed_mph",
        "tip_pct",
        "weekday_name",
        "distance_band",
        "anomaly_flag",
    ]
    # Filtra apenas colunas que existem no df (seguranca contra schema differences)
    colunas_existentes = [c for c in COLUNAS_TABELA if c in df.columns]

    st.dataframe(
        df[colunas_existentes].head(MAX_LINHAS_TABELA),
        use_container_width=True,
    )

# ========================= TAB: POR HORA (Passo 8 — esqueleto) ================ #
with tab_hora:
    st.info("View detalhada por hora — sera implementada no Passo 8.")

# ========================= TAB: POR FORNECEDOR (Passo 8 — esqueleto) ========== #
with tab_vendor:
    st.info("View detalhada por fornecedor — sera implementada no Passo 8.")

# ========================= TAB: POR PAGAMENTO (Passo 8 — esqueleto) =========== #
with tab_pagamento:
    st.info("View detalhada por tipo de pagamento — sera implementada no Passo 8.")

# ========================= TAB: POR DIA DA SEMANA (Passo 8 — esqueleto) ======= #
with tab_semana:
    st.info("View detalhada por dia da semana — sera implementada no Passo 8.")
