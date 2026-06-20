"""Testes do pipeline ETL. Evoluem a cada passo implementado."""

from pathlib import Path

import pandas as pd

from src.Extract import read_csv
from src.Load import load


def test_read_csv_returns_dataframe(tmp_path: Path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "passenger_count,trip_distance,fare_amount,tpep_pickup_datetime\n"
        "1,2.5,12.0,2016-01-01 08:00:00\n"
    )

    df = read_csv(str(csv_path))

    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 1
    assert "fare_amount" in df.columns


def test_load_writes_parquet(tmp_path: Path):
    df = pd.DataFrame({"pickup_date": ["2016-01-01"], "total_rides": [1]})
    output_path = tmp_path / "output.parquet"

    written = load(df, output_path)

    assert written.exists()
    loaded = pd.read_parquet(written)
    assert loaded.loc[0, "total_rides"] == 1
