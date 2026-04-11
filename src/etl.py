import argparse
from pathlib import Path

import pandas as pd


def extract(csv_path: Path) -> pd.DataFrame:
    """Extrai dados de um CSV para um DataFrame."""
    return pd.read_csv(csv_path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma os dados aplicando limpeza e agregações."""
    df = df.copy()

    # Exemplo de transformação simples para dados de corridas de táxi
    if "passenger_count" in df.columns:
        df["passenger_count"] = df["passenger_count"].fillna(0).astype(int)

    if "trip_distance" in df.columns:
        df["trip_distance"] = df["trip_distance"].fillna(0.0).astype(float)

    if "fare_amount" in df.columns:
        df["fare_amount"] = df["fare_amount"].fillna(0.0).astype(float)

    if "tpep_pickup_datetime" in df.columns:
        df["pickup_date"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce").dt.date

    # Agregação por dia de corrida
    if "pickup_date" in df.columns and "fare_amount" in df.columns:
        df = (
            df.groupby("pickup_date", as_index=False)
            .agg(
                total_rides=("fare_amount", "size"),
                total_fare=("fare_amount", "sum"),
                mean_fare=("fare_amount", "mean"),
                total_distance=("trip_distance", "sum"),
            )
        )

    return df


def load(df: pd.DataFrame, output_path: Path) -> None:
    """Carrega os dados transformados em um arquivo Parquet."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline ETL simples para dados de táxi")
    parser.add_argument("--input", required=True, help="Caminho do arquivo CSV de entrada")
    parser.add_argument("--output", required=True, help="Caminho do arquivo Parquet de saída")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df_raw = extract(input_path)
    df_transformed = transform(df_raw)
    load(df_transformed, output_path)

    print(f"ETL concluído: {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
