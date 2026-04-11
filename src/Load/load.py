from pathlib import Path


def load(df, output_path: Path) -> None:
    """Carrega os dados transformados em um arquivo Parquet."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
