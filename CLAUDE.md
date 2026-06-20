# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado atual do projeto

O repositório foi **reiniciado do zero** no commit `b6e93af "Refazendo projeto"` — o HEAD
não contém código-fonte. Há uma implementação anterior preservada no histórico (commit
`d85552d`) usada apenas como referência de estilo. O plano de implementação completo (9
passos do desafio) está em `~/.claude/plans/quero-que-voc-gera-wild-tower.md` e é a fonte de
verdade do que construir.

Trata-se do **Desafio técnico 02 — ETL Simples com Dados de Táxi de NYC** (comunidade Dados
por Todos): um pipeline ETL sobre o dataset NYC Yellow Taxi, terminando em um dashboard
Streamlit.

## Stack e ambiente

- **Python 3.14**, gerenciado com **`uv`** rodando em **Windows nativo (sem WSL)**.
- Dependências: `pandas>=2.2,<3`, `pyarrow>=19`, `ipykernel>=7.2`, `streamlit>=1.44.1`,
  `kagglehub` (extração). Testes com `pytest`.
- Toda execução é via `uv run` para usar o ambiente do projeto.

### Comandos

```bash
# setup inicial (uma vez)
uv python install 3.14
uv sync                         # instala deps do pyproject.toml/uv.lock

# pipeline ETL completo (gera data/output/trips.parquet)
uv run python etl.py

# dashboard
uv run streamlit run dashboard.py

# testes
uv run pytest                   # todos
uv run pytest tests/test_etl.py::test_transform_aggregates_by_date   # um único teste
```

> O download do dataset usa kagglehub e exige credenciais Kaggle: `kaggle.json` em
> `%USERPROFILE%\.kaggle\` ou as variáveis `KAGGLE_USERNAME`/`KAGGLE_KEY`. Os CSVs são
> grandes (~2 GB cada) — use amostragem (`nrows`) em desenvolvimento.

## Arquitetura (alvo)

Pipeline modular com uma **única fonte de verdade**: `data/output/trips.parquet`
(nível de corrida, limpo e enriquecido). Ordem do fluxo em `etl.py`:

```
Kaggle CSV → Extract → Validate → Transform → Load(Parquet) → Dashboard/Views
```

Pacotes em `src/`, um por etapa do pipeline (cada um mapeia para um passo do desafio):

- `src/Extract/` — leitura do CSV via kagglehub → DataFrame (Passo 2).
- `src/Validate/` — conversão de datas, regras de anomalia combinadas em **máscara OR
  única**, filtro dos válidos e **quality score** por lote (Passo 3).
- `src/Transform/` — colunas derivadas (data/hora/turno, velocidade, tip_pct, faixas,
  rentabilidade), tratando divisão por zero com `replace(0, NaN)` → cálculo → `fillna(0)`
  (Passo 4).
- `src/Aggregate/` — métricas e agregações (por dia/semana/turno/vendor/rota, percentis).
  **Reutilizado pelo `dashboard.py`** para montar as views, evitando duplicar lógica (Passo 5).
- `src/Load/` — persistência em Parquet com engine pyarrow; converte `date` para texto e
  remove timestamps textuais antes de gravar (Passo 6).
- `dashboard.py` — app Streamlit que lê o Parquet e renderiza KPIs + views por hora,
  fornecedor, pagamento e dia da semana (Passos 7 e 8).

`etl.py` é o orquestrador (CLI) que encadeia extract→validate→transform→load.

### Notas sobre os dados

- Dataset Kaggle: `elemento/nyc-yellow-taxi-trip-data` (jan/2015 e jan–mar/2016).
- Esta versão **tem coordenadas lat/long** (`pickup_longitude`, `pickup_latitude`,
  `dropoff_longitude`, `dropoff_latitude`) — por isso a validação inclui bounding box de NYC
  (lon ∈ [−74.3, −73.7], lat ∈ [40.5, 40.9]). Centralize constantes assim em `src/config.py`.
- Timestamps: `tpep_pickup_datetime` / `tpep_dropoff_datetime`.
- BigQuery aparece na stack geral do desafio, mas **nenhum dos 9 passos o usa** — a
  persistência é Parquet local. Tratar BigQuery como evolução futura, fora do escopo padrão.

## Subagents disponíveis (`.claude/agents/`)

- **python-project-engineer** — implementa/avança o projeto Python conforme o plano.
- **bigquery-sql-expert** — escreve/otimiza/revisa BigQuery Standard SQL (só se BigQuery
  entrar no escopo).
- **mussum-streamlit-dev** — especialista em Streamlit; responde no estilo do Mussum.
