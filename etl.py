"""Orquestrador do pipeline ETL do NYC Yellow Taxi.

Fluxo: extract -> validate -> transform -> load (Parquet).
Uso:
    uv run python etl.py                 # arquivo e saída padrão
    uv run python etl.py --nrows 100000  # amostra para desenvolvimento
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src import config
from src.Extract import extract
from src.Validate import validate
from src.Transform import transform
from src.Load import load


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
    parser = argparse.ArgumentParser(description="Pipeline ETL — NYC Yellow Taxi")
    parser.add_argument("--input", default=config.DEFAULT_CSV, help="CSV do dataset Kaggle")
    parser.add_argument("--output", default=str(config.TRIPS_PARQUET), help="Parquet de saída")
    parser.add_argument("--nrows", type=int, default=None, help="Ler apenas N linhas (dev)")
    args = parser.parse_args()

    run(args.input, Path(args.output), args.nrows)


if __name__ == "__main__":
    main()
