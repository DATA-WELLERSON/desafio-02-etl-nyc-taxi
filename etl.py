"""Orquestrador do pipeline ETL do NYC Yellow Taxi.

Fluxo: extract -> validate -> transform -> load (Parquet).

Configure os parâmetros abaixo (seção CONFIGURAÇÃO) e rode:
    uv run python etl.py
"""

from __future__ import annotations

from pathlib import Path

from src import config
from src.Extract import extract
from src.Validate import validate
from src.Transform import transform
from src.Load import load

# --------------------------------------------------------------------------- #
# CONFIGURAÇÃO — edite estas variáveis (em vez de passar argumentos no terminal)
# --------------------------------------------------------------------------- #

# Arquivo CSV do dataset Kaggle a processar.
INPUT_FILE: str = config.DEFAULT_CSV

# Caminho do Parquet de saída.
OUTPUT_PATH: Path = config.TRIPS_PARQUET

# Quantas linhas ler. Use um número (ex.: 100_000) para amostra em desenvolvimento,
# pois os arquivos têm ~2 GB. Use None para ler o arquivo inteiro.
NROWS: int | None = 100_000

# --------------------------------------------------------------------------- #


def run(file_path: str, output_path: Path, nrows: int | None) -> Path:
    print(f"[1/4] Extraindo '{file_path}'" + (f" (nrows={nrows})" if nrows else "") + " ...")
    df = extract(file_path=file_path, nrows=nrows)
    print(f"      {len(df):,} linhas brutas carregadas.")

    print("[2/4] Validando ...")
    df, report = validate(df)
    print(f"      {report.get('rows_out', len(df)):,} linhas válidas.")

    print("[3/4] Transformando ...")
    df = transform(df)

    print("[4/4] Persistindo em Parquet ...")
    written = load(df, output_path)
    print(f"      Salvo em {written}")
    return written


def main() -> None:
    run(INPUT_FILE, OUTPUT_PATH, NROWS)


if __name__ == "__main__":
    main()
