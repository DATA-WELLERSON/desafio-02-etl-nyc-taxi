from pathlib import Path

import pandas as pd


def extract(csv_path: Path) -> pd.DataFrame:
    """Extrai dados de um CSV para um DataFrame."""
    return pd.read_csv(csv_path)
