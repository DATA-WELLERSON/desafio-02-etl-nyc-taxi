from pathlib import Path

import pandas as pd

from src.etl import extract, load, transform


def test_extract_returns_dataframe(tmp_path: Path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("passenger_count,trip_distance,fare_amount,tpep_pickup_datetime\n1,2.5,12.0,2024-04-01 08:00:00\n")

    df = extract(csv_path)

    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 1
    assert "fare_amount" in df.columns


def test_transform_aggregates_by_date():
    df = pd.DataFrame(
        {
            "passenger_count": [1, 2],
            "trip_distance": [3.2, 4.8],
            "fare_amount": [10.0, 15.0],
            "tpep_pickup_datetime": ["2024-04-01 09:00:00", "2024-04-01 10:00:00"],
        }
    )

    result = transform(df)

    assert "pickup_date" in result.columns
    assert result.loc[0, "total_rides"] == 2
    assert result.loc[0, "total_fare"] == 25.0


def test_load_writes_parquet(tmp_path: Path):
    df = pd.DataFrame({"pickup_date": ["2024-04-01"], "total_rides": [1]})
    output_path = tmp_path / "output.parquet"

    load(df, output_path)

    assert output_path.exists()
    loaded = pd.read_parquet(output_path)
    assert loaded.loc[0, "total_rides"] == 1
