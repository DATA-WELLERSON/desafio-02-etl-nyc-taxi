"""Constantes centrais do pipeline ETL do NYC Yellow Taxi."""

from __future__ import annotations

from pathlib import Path

# ----------------------------------------------------------------------------- #
# Caminhos
# ----------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
TRIPS_PARQUET = OUTPUT_DIR / "trips.parquet"
METRICS_DIR = OUTPUT_DIR / "metrics"

# ----------------------------------------------------------------------------- #
# Fonte de dados (Kaggle)
# ----------------------------------------------------------------------------- #
KAGGLE_DATASET = "elemento/nyc-yellow-taxi-trip-data"
# Arquivo padrão usado no pipeline (jan/2016). Os demais meses seguem o mesmo schema.
DEFAULT_CSV = "yellow_tripdata_2016-01.csv"

# ----------------------------------------------------------------------------- #
# Schema / colunas relevantes
# ----------------------------------------------------------------------------- #
PICKUP_DATETIME = "tpep_pickup_datetime"
DROPOFF_DATETIME = "tpep_dropoff_datetime"

PICKUP_LON = "pickup_longitude"
PICKUP_LAT = "pickup_latitude"
DROPOFF_LON = "dropoff_longitude"
DROPOFF_LAT = "dropoff_latitude"

# ----------------------------------------------------------------------------- #
# Bounding box de NYC (descarta coordenadas fora da cidade)
# ----------------------------------------------------------------------------- #
NYC_LON_MIN, NYC_LON_MAX = -74.3, -73.7
NYC_LAT_MIN, NYC_LAT_MAX = 40.5, 40.9

# ----------------------------------------------------------------------------- #
# Regras de anomalia (faixas plausíveis de negócio)
# ----------------------------------------------------------------------------- #
MIN_TRIP_DISTANCE = 0.0          # milhas; <= 0 é inválido
MAX_TRIP_DISTANCE = 100.0        # milhas
MIN_PASSENGERS = 1
MAX_PASSENGERS = 6
MIN_FARE = 0.0                   # USD; <= 0 é inválido
MAX_FARE = 500.0                 # USD
MIN_DURATION_MIN = 1.0           # minutos
MAX_DURATION_MIN = 180.0         # minutos
MAX_SPEED_MPH = 80.0             # milhas/hora

# Consistência financeira: total_amount ~= soma dos componentes
FINANCIAL_TOLERANCE = 0.05       # USD

# ----------------------------------------------------------------------------- #
# Domínios de categorias permitidas
# ----------------------------------------------------------------------------- #
VALID_VENDOR_IDS = {1, 2}
VALID_PAYMENT_TYPES = {1, 2, 3, 4, 5, 6}
VALID_RATECODE_IDS = {1, 2, 3, 4, 5, 6}

# Componentes que somam total_amount
FARE_COMPONENTS = [
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
]

# ----------------------------------------------------------------------------- #
# Turnos do dia (faixa de hora -> rótulo)
# ----------------------------------------------------------------------------- #
SHIFTS = [
    (0, 6, "madrugada"),
    (6, 12, "manha"),
    (12, 18, "tarde"),
    (18, 24, "noite"),
]

# ----------------------------------------------------------------------------- #
# Transform — faixas, calendário e flags (Passo 4)
# ----------------------------------------------------------------------------- #
# Nomes dos dias da semana (índice 0=segunda ... 6=domingo, como em dt.weekday).
WEEKDAY_NAMES = [
    "segunda",
    "terca",
    "quarta",
    "quinta",
    "sexta",
    "sabado",
    "domingo",
]

# Faixas de distância (milhas) -> rótulo.
DISTANCE_BAND_BINS = [0, 2, 6, float("inf")]
DISTANCE_BAND_LABELS = ["curta", "media", "longa"]

# Faixas de duração (minutos) -> rótulo.
DURATION_BAND_BINS = [0, 5, 30, float("inf")]
DURATION_BAND_LABELS = ["muito_curta", "normal", "longa"]

# Flag de anomalia combinada: velocidade alta E tarifa baixa ao mesmo tempo.
ANOMALY_SPEED_MPH = 60.0
ANOMALY_FARE = 5.0
