import logging
import numpy as np
import pandas as pd
from pathlib import Path
from src.config import (
    FACT_SHOTS_CSV,
    DIM_PLAYER_CSV,
    DIM_SHOT_ZONE_CSV,
    SUMMARY_STATS_CSV
)

logger = logging.getLogger(__name__)

def compute_shot_angles(df: pd.DataFrame) -> pd.Series:
    """Calculate shot angle in degrees relative to the hoop (-90 deg to +90 deg)."""
    # LOC_X is lateral (-250 to 250), LOC_Y is distance from baseline (-52 to 418)
    angles_rad = np.arctan2(df['LOC_X'], df['LOC_Y'])
    angles_deg = np.degrees(angles_rad)
    return np.round(angles_deg, 2)

def process_spatial_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Perform spatial feature engineering, coordinate mapping, and EV metric calculations.
    """
    df = df_raw.copy()
    logger.info("Processing spatial features and Expected Value metrics...")

    # 1. Shot Value & Actual Points Scored
    df['SHOT_VALUE'] = df['SHOT_TYPE'].apply(lambda x: 3 if '3PT' in str(x) else 2)
    df['POINTS_SCORED'] = df['SHOT_MADE_FLAG'] * df['SHOT_VALUE']

    # 2. Shot Angle (Degrees)
    df['SHOT_ANGLE_DEG'] = compute_shot_angles(df)

    # 3. Power BI Court Coordinates Mapping
    # Raw LOC_X is in 1/10th feet [-250, 250]. Convert to [0, 50] feet court width.
    df['POWERBI_X'] = np.round((df['LOC_X'] + 250) / 10.0, 2)
    # Raw LOC_Y is in 1/10th feet [-52, 418]. Convert to [0, 47] feet half-court depth.
    df['POWERBI_Y'] = np.round((df['LOC_Y'] + 52) / 10.0, 2)

    # 4. Spatial Zone Baseline FG% and Expected Value (EV)
    zone_group = df.groupby(['SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA'])
    zone_stats = zone_group.agg(
        ZONE_TOTAL_SHOTS=('SHOT_MADE_FLAG', 'count'),
        ZONE_TOTAL_MAKES=('SHOT_MADE_FLAG', 'sum'),
        ZONE_BASELINE_FG_PCT=('SHOT_MADE_FLAG', 'mean')
    ).reset_index()

    zone_stats['ZONE_BASELINE_FG_PCT'] = np.round(zone_stats['ZONE_BASELINE_FG_PCT'], 4)

    # Merge zone baselines back to shot facts
    df = df.merge(zone_stats, on=['SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA'], how='left')

    # Expected Value (EV) = SHOT_VALUE * ZONE_BASELINE_FG_PCT
    df['EXPECTED_VALUE'] = np.round(df['SHOT_VALUE'] * df['ZONE_BASELINE_FG_PCT'], 4)

    # Points Above Expected (PAE) = Actual Points - Expected Value
    df['POINTS_ABOVE_EXPECTED'] = np.round(df['POINTS_SCORED'] - df['EXPECTED_VALUE'], 4)

    # Add Shot ID
    df.insert(0, 'SHOT_ID', range(1, len(df) + 1))

    logger.info("Spatial feature engineering complete.")
    return df

def generate_dim_player(df_facts: pd.DataFrame) -> pd.DataFrame:
    """Generate Dim_Player table with player-level spatial efficiency aggregations."""
    logger.info("Generating Dim_Player dimension table...")
    
    player_group = df_facts.groupby('PLAYER_NAME')
    
    dim_player = player_group.agg(
        TOTAL_SHOTS=('SHOT_MADE_FLAG', 'count'),
        TOTAL_MAKES=('SHOT_MADE_FLAG', 'sum'),
        TOTAL_POINTS=('POINTS_SCORED', 'sum'),
        FG_PCT=('SHOT_MADE_FLAG', 'mean'),
        TOTAL_EXPECTED_POINTS=('EXPECTED_VALUE', 'sum'),
        TOTAL_PAE=('POINTS_ABOVE_EXPECTED', 'sum'),
        AVG_SHOT_DISTANCE=('SHOT_DISTANCE', 'mean')
    ).reset_index()

    # 3PT Statistics
    df_3pt = df_facts[df_facts['SHOT_VALUE'] == 3].groupby('PLAYER_NAME').agg(
        SHOTS_3PT=('SHOT_MADE_FLAG', 'count'),
        MAKES_3PT=('SHOT_MADE_FLAG', 'sum'),
        PCT_3PT=('SHOT_MADE_FLAG', 'mean')
    ).reset_index()

    # Merge 3PT stats
    dim_player = dim_player.merge(df_3pt, on='PLAYER_NAME', how='left').fillna({
        'SHOTS_3PT': 0, 'MAKES_3PT': 0, 'PCT_3PT': 0.0
    })

    # Calculate eFG% = (FGM + 0.5 * 3PM) / FGA
    dim_player['eFG_PCT'] = np.round(
        (dim_player['TOTAL_MAKES'] + 0.5 * dim_player['MAKES_3PT']) / dim_player['TOTAL_SHOTS'], 4
    )

    dim_player['FG_PCT'] = np.round(dim_player['FG_PCT'], 4)
    dim_player['PCT_3PT'] = np.round(dim_player['PCT_3PT'], 4)
    dim_player['TOTAL_EXPECTED_POINTS'] = np.round(dim_player['TOTAL_EXPECTED_POINTS'], 2)
    dim_player['TOTAL_PAE'] = np.round(dim_player['TOTAL_PAE'], 2)
    dim_player['PAE_PER_SHOT'] = np.round(dim_player['TOTAL_PAE'] / dim_player['TOTAL_SHOTS'], 4)
    dim_player['AVG_SHOT_DISTANCE'] = np.round(dim_player['AVG_SHOT_DISTANCE'], 2)

    dim_player.sort_values(by='TOTAL_POINTS', ascending=False, inplace=True)
    return dim_player

def generate_dim_shot_zone(df_facts: pd.DataFrame) -> pd.DataFrame:
    """Generate Dim_Shot_Zone table with zone metrics."""
    logger.info("Generating Dim_Shot_Zone dimension table...")
    
    zone_group = df_facts.groupby(['SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA'])
    
    dim_zone = zone_group.agg(
        TOTAL_ATTEMPTS=('SHOT_MADE_FLAG', 'count'),
        TOTAL_MAKES=('SHOT_MADE_FLAG', 'sum'),
        ZONE_BASELINE_FG_PCT=('SHOT_MADE_FLAG', 'mean'),
        AVG_SHOT_VALUE=('SHOT_VALUE', 'mean'),
        AVG_EXPECTED_VALUE=('EXPECTED_VALUE', 'mean'),
        TOTAL_POINTS_SCORED=('POINTS_SCORED', 'sum')
    ).reset_index()

    dim_zone['ZONE_BASELINE_FG_PCT'] = np.round(dim_zone['ZONE_BASELINE_FG_PCT'], 4)
    dim_zone['AVG_EXPECTED_VALUE'] = np.round(dim_zone['AVG_EXPECTED_VALUE'], 4)
    dim_zone['ZONE_PAE'] = np.round(dim_zone['TOTAL_POINTS_SCORED'] - (dim_zone['TOTAL_ATTEMPTS'] * dim_zone['AVG_EXPECTED_VALUE']), 2)

    dim_zone.sort_values(by='TOTAL_ATTEMPTS', ascending=False, inplace=True)
    return dim_zone

def export_processed_datasets(df_facts: pd.DataFrame) -> dict:
    """
    Generate all star-schema tables and write to processed directory.
    """
    dim_player = generate_dim_player(df_facts)
    dim_zone = generate_dim_shot_zone(df_facts)

    # Save CSV files
    df_facts.to_csv(FACT_SHOTS_CSV, index=False)
    dim_player.to_csv(DIM_PLAYER_CSV, index=False)
    dim_zone.to_csv(DIM_SHOT_ZONE_CSV, index=False)
    
    # Save Zone Summary file
    dim_zone.to_csv(SUMMARY_STATS_CSV, index=False)

    logger.info(f"Fact_Shots saved to {FACT_SHOTS_CSV} ({len(df_facts)} rows)")
    logger.info(f"Dim_Player saved to {DIM_PLAYER_CSV} ({len(dim_player)} rows)")
    logger.info(f"Dim_Shot_Zone saved to {DIM_SHOT_ZONE_CSV} ({len(dim_zone)} rows)")

    return {
        'fact_shots': df_facts,
        'dim_player': dim_player,
        'dim_shot_zone': dim_zone
    }
