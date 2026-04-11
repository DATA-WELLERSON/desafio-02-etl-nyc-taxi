import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter


class Extractor:
    """Classe responsável por extrair dados de diferentes fontes para um DataFrame."""

    def __init__(self, file_path: str, elemento: str):
        self.file_path = file_path
        self.elemento = elemento

    def read_from_kaggle(self) -> pd.DataFrame:
        """Carrega o dataset do Kaggle e retorna um DataFrame."""
        file_path = self.file_path

        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            self.elemento,
            file_path,
        )

        return df

    
