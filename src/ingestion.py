import time
import logging
import pandas as pd
from pathlib import Path
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster, shotchartdetail
from src.config import (
    TEAM_ABBREVIATION,
    SEASON,
    SEASON_TYPE,
    API_TIMEOUT,
    API_RETRY_LIMIT,
    API_REQUEST_DELAY,
    API_RETRY_DELAY,
    RAW_SHOTS_CSV
)

logger = logging.getLogger(__name__)

def fetch_team_id(team_abbr: str = TEAM_ABBREVIATION) -> int:
    """Fetch official NBA team ID by abbreviation."""
    nba_teams = teams.get_teams()
    matched = [t for t in nba_teams if t['abbreviation'] == team_abbr]
    if not matched:
        raise ValueError(f"Team abbreviation '{team_abbr}' not found in NBA API static team list.")
    team_id = matched[0]['id']
    logger.info(f"Resolved team abbreviation '{team_abbr}' to Team ID: {team_id}")
    return team_id

def fetch_team_roster(team_id: int, season: str = SEASON) -> pd.DataFrame:
    """Fetch official roster for team and season."""
    logger.info(f"Fetching team roster for Season {season}...")
    roster_endpoint = commonteamroster.CommonTeamRoster(team_id=team_id, season=season, timeout=API_TIMEOUT)
    roster_df = roster_endpoint.get_data_frames()[0]
    logger.info(f"Retrieved {len(roster_df)} players on roster.")
    return roster_df

def fetch_player_shots(team_id: int, player_id: int, player_name: str, season: str = SEASON) -> pd.DataFrame:
    """Fetch shot chart details for a single player with retry logic."""
    attempts = 0
    while attempts < API_RETRY_LIMIT:
        try:
            logger.info(f"Fetching shot data for {player_name} (ID: {player_id})...")
            shot_endpoint = shotchartdetail.ShotChartDetail(
                team_id=team_id,
                player_id=player_id,
                context_measure_simple='FGA',
                season_nullable=season,
                season_type_all_star=SEASON_TYPE,
                timeout=API_TIMEOUT
            )
            df_shots = shot_endpoint.get_data_frames()[0]
            logger.info(f"Successfully retrieved {len(df_shots)} shots for {player_name}.")
            return df_shots
        except Exception as e:
            attempts += 1
            logger.warning(f"Timeout/Error for {player_name} (Attempt {attempts}/{API_RETRY_LIMIT}): {e}")
            if attempts < API_RETRY_LIMIT:
                time.sleep(API_RETRY_DELAY)
            else:
                logger.error(f"Failed to retrieve shot data for {player_name} after {API_RETRY_LIMIT} attempts.")
                return pd.DataFrame()

def ingest_raw_shots(force_refresh: bool = False) -> pd.DataFrame:
    """
    Orchestrate raw shot data extraction.
    If RAW_SHOTS_CSV exists and force_refresh is False, loads from disk cache.
    Otherwise queries NBA API.
    """
    if RAW_SHOTS_CSV.exists() and not force_refresh:
        logger.info(f"Loading raw shot dataset from cache: {RAW_SHOTS_CSV}")
        return pd.read_csv(RAW_SHOTS_CSV)

    logger.info("Starting fresh raw shot extraction from NBA Stats API...")
    team_id = fetch_team_id()
    roster_df = fetch_team_roster(team_id)

    all_shots = []
    for _, player in roster_df.iterrows():
        p_id = player['PLAYER_ID']
        p_name = player['PLAYER']
        df_player = fetch_player_shots(team_id=team_id, player_id=p_id, player_name=p_name)
        if not df_player.empty:
            all_shots.append(df_player)
        time.sleep(API_REQUEST_DELAY)

    if not all_shots:
        raise RuntimeError("No shot data was extracted from NBA API.")

    df_master = pd.concat(all_shots, ignore_index=True)
    
    # Selected columns to clean API response
    cols_to_keep = [
        'PLAYER_NAME', 'GAME_DATE', 'ACTION_TYPE', 'SHOT_TYPE',
        'SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_DISTANCE',
        'LOC_X', 'LOC_Y', 'SHOT_MADE_FLAG'
    ]
    
    # Filter available columns
    available_cols = [c for c in cols_to_keep if c in df_master.columns]
    df_clean = df_master[available_cols].copy()

    # Save to raw directory
    RAW_SHOTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(RAW_SHOTS_CSV, index=False)
    logger.info(f"Raw dataset exported successfully to {RAW_SHOTS_CSV} ({len(df_clean)} rows).")

    return df_clean
