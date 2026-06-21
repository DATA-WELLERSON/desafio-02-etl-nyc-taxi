# ETL Simples — NYC Yellow Taxi

Pipeline ETL sobre o dataset **NYC Yellow Taxi** (Desafio técnico 02 — comunidade
**Dados por Todos**). Extrai os dados brutos do Kaggle, valida a qualidade, transforma e
enriquece, persiste em Parquet e exibe tudo em um dashboard Streamlit.

## Stack

Python 3.14 · pandas · pyarrow · streamlit · kagglehub — gerenciado com **`uv`** em
Windows nativo.

## Setup

```bash
uv python install 3.14
uv sync
```

Configure as credenciais do Kaggle (`kaggle.json` em `%USERPROFILE%\.kaggle\` ou as
variáveis `KAGGLE_USERNAME` / `KAGGLE_KEY`) para o download automático do dataset.

## Como rodar

```bash
# pipeline completo (gera data/output/trips.parquet)
uv run python etl.py

# dashboard
uv run streamlit run dashboard.py

# testes
uv run pytest
```

Os parâmetros do pipeline (arquivo CSV, caminho de saída e `NROWS`) são
configurados editando a seção **CONFIGURAÇÃO** no topo do `etl.py`. Como os CSVs
têm ~2 GB, use `NROWS = 100_000` para uma amostra em desenvolvimento e `NROWS = None`
para processar o arquivo inteiro.

## Estrutura

```
etl.py            # orquestrador: extract -> validate -> transform -> load
dashboard.py      # app Streamlit (KPIs + views)
src/
  config.py       # constantes (dataset, bbox NYC, regras, faixas, paths)
  derive.py       # cálculos compartilhados (duração, velocidade, divisão segura)
  Extract/        # leitura do CSV via kagglehub
  Validate/       # regras de anomalia + quality score
  Transform/      # novas colunas (hora, turno, velocidade, faixas...)
  Aggregate/      # métricas e agregações (reutilizado pelo dashboard)
  Load/           # persistência em Parquet
tests/            # pytest
data/input|output # dados brutos / gerados (gitignored)
```

Fluxo: `Kaggle CSV → Extract → Validate → Transform → Load(Parquet) → Dashboard`.
Fonte única de verdade: `data/output/trips.parquet` (nível de corrida, limpo e enriquecido).
