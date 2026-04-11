import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma os dados aplicando limpeza e agregações."""
    df = df.copy()

    if "passenger_count" in df.columns:
        df["passenger_count"] = df["passenger_count"].fillna(0).astype(int)

    if "trip_distance" in df.columns:
        df["trip_distance"] = df["trip_distance"].fillna(0.0).astype(float)

    if "fare_amount" in df.columns:
        df["fare_amount"] = df["fare_amount"].fillna(0.0).astype(float)

    if "tpep_pickup_datetime" in df.columns:
        df["pickup_date"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce").dt.date

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
