"""Testes do pipeline ETL. Evoluem a cada passo implementado."""

from pathlib import Path

import pandas as pd

from src.Extract import read_csv
from src.Load import load
from src.Transform import transform
from src.Validate import validate


def _valid_row() -> dict:
    """Uma corrida plausível (passa em todas as regras de validação)."""
    return {
        "tpep_pickup_datetime": "2016-01-01 08:00:00",
        "tpep_dropoff_datetime": "2016-01-01 08:20:00",  # 20 min
        "passenger_count": 1,
        "trip_distance": 3.0,
        "pickup_longitude": -73.99,
        "pickup_latitude": 40.75,
        "dropoff_longitude": -73.96,
        "dropoff_latitude": 40.78,
        "VendorID": 1,
        "payment_type": 1,
        "RatecodeID": 1,
        "fare_amount": 14.0,
        "extra": 0.5,
        "mta_tax": 0.5,
        "tip_amount": 2.0,
        "tolls_amount": 0.0,
        "improvement_surcharge": 0.3,
        "total_amount": 17.3,  # = soma dos componentes
    }


def test_validate_or_mask_removes_anomalies():
    bom = _valid_row()

    fora_bbox = _valid_row()
    fora_bbox["pickup_longitude"] = -80.0  # fora de NYC

    distancia_zero = _valid_row()
    distancia_zero["trip_distance"] = 0.0  # <= 0 é inválido

    df = pd.DataFrame([bom, fora_bbox, distancia_zero])

    df_valid, report = validate(df)

    assert report["rows_in"] == 3
    assert report["rows_out"] == 1  # só a linha boa sobra
    assert report["failures_by_rule"]["coord_pickup"] == 1
    assert report["failures_by_rule"]["distancia"] == 1
    # quality score = 1/3 das linhas aprovadas
    assert report["quality_score"] == round(100 / 3, 2)


def test_validate_keeps_clean_batch_with_full_score():
    df = pd.DataFrame([_valid_row(), _valid_row()])

    df_valid, report = validate(df)

    # 2 linhas iguais: a 2ª é marcada como duplicada -> sobra 1.
    assert report["failures_by_rule"]["duplicado"] == 1
    assert report["rows_out"] == 1


def test_validate_drops_rows_with_nulls():
    bom = _valid_row()

    distancia_nula = _valid_row()
    distancia_nula["trip_distance"] = None  # nulo deve reprovar, não escapar

    coord_nula = _valid_row()
    coord_nula["pickup_latitude"] = None

    df = pd.DataFrame([bom, distancia_nula, coord_nula])

    df_valid, report = validate(df)

    assert report["rows_out"] == 1  # só a linha boa sobra
    assert report["failures_by_rule"]["distancia"] == 1
    assert report["failures_by_rule"]["coord_pickup"] == 1


def test_validate_raises_on_missing_columns():
    import pytest

    df = pd.DataFrame({"trip_distance": [1.0]})  # faltam quase todas as colunas

    with pytest.raises(ValueError, match="Colunas ausentes"):
        validate(df)


def test_transform_creates_temporal_and_derived_columns():
    out = transform(pd.DataFrame([_valid_row()]))
    row = out.iloc[0]

    # Temporais (2016-01-01 08:00 é uma sexta-feira de manhã)
    assert row["pickup_date"] == "2016-01-01"
    assert row["pickup_hour"] == 8
    assert row["weekday"] == 4
    assert row["weekday_name"] == "sexta"
    assert bool(row["is_weekend"]) is False
    assert row["shift"] == "manha"

    # Métricas: 3 milhas em 20 min (1/3 h) = 9 mph; gorjeta 2/14
    assert row["duration_min"] == 20.0
    assert row["speed_mph"] == 9.0
    assert row["tip_pct"] == round(2.0 / 14.0 * 100, 2)

    # Faixas
    assert row["distance_band"] == "media"   # 3 milhas
    assert row["duration_band"] == "normal"  # 20 min


def test_transform_handles_division_by_zero():
    r = _valid_row()
    r["fare_amount"] = 0.0     # tip_pct não pode virar inf/NaN
    r["trip_distance"] = 0.0   # revenue_per_mile/speed idem

    row = transform(pd.DataFrame([r])).iloc[0]

    assert row["tip_pct"] == 0.0
    assert row["revenue_per_mile"] == 0.0
    assert row["speed_mph"] == 0.0


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
