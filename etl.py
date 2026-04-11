import argparse
from pathlib import Path

try:
    from .src.Extract.extract import extract
    from .src.Transform.transform import transform
    from .src.Load.load import load
except ImportError:
    from Extract.extract import extract
    from Transform.transform import transform
    from Load.load import load


def main() -> None:
   


    print('Olá, este é um pipeline ETL simples para dados de táxi. ' \
    'Por favor, forneça os caminhos de entrada e saída usando os argumentos --input e --output.')


if __name__ == "__main__":
    main()
