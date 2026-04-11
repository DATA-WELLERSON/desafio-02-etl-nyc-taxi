# ETL Simples em Python

Este projeto é um exemplo básico de pipeline ETL em Python para dados de táxi de NYC.

## Estrutura do projeto

- `src/etl.py`: código principal do ETL com funções `extract`, `transform`, `load` e `main`
- `data/input/`: entrada de dados (CSV)
- `data/output/`: saída de dados processados
- `tests/test_etl.py`: testes unitários simples do pipeline
- `requirements.txt`: dependências do projeto

## Como usar

1. Instale dependências:

```bash
python -m pip install -r requirements.txt
```

2. Coloque o CSV de entrada em `data/input/taxi_data.csv`.

3. Execute o pipeline:

```bash
python src/etl.py --input data/input/taxi_data.csv --output data/output/taxi_summary.parquet
```

4. Verifique o resultado em `data/output/taxi_summary.parquet`.

## Testes

```bash
pytest
```
