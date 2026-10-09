from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOG_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Data Extraction Target Settings
TEAM_ABBREVIATION = "GSW"
SEASON = "2021-22"
SEASON_TYPE = "Regular Season"

# API & Networking Config
API_TIMEOUT = 60
API_RETRY_LIMIT = 3
API_REQUEST_DELAY = 1.0  # seconds between player requests
API_RETRY_DELAY = 5.0    # seconds backoff on timeout

# File Paths
RAW_SHOTS_CSV = RAW_DATA_DIR / "gsw_2022_roster_shots.csv"
FACT_SHOTS_CSV = PROCESSED_DATA_DIR / "fact_shots.csv"
DIM_PLAYER_CSV = PROCESSED_DATA_DIR / "dim_player.csv"
DIM_SHOT_ZONE_CSV = PROCESSED_DATA_DIR / "dim_shot_zone.csv"
SUMMARY_STATS_CSV = PROCESSED_DATA_DIR / "spatial_zone_ev_summary.csv"
LOG_FILE = LOG_DIR / "etl_pipeline.log"

# NBA Court Dimension Constants for Power BI Coordinate Mapping
# NBA Court: 50ft wide (-250 to 250 in LOC_X tenths of a foot)
# Half Court: 47ft deep (-52 to 418 in LOC_Y tenths of a foot)
COURT_X_MIN = -250
COURT_X_MAX = 250
COURT_Y_MIN = -52
COURT_Y_MAX = 418
