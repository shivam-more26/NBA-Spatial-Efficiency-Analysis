import sys
import argparse
import logging
from pathlib import Path
from src.config import LOG_FILE
from src.ingestion import ingest_raw_shots
from src.processing import process_spatial_features, export_processed_datasets

def setup_logging():
    """Configure logger with stream and file handlers."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_etl_pipeline(force_refresh: bool = False):
    """Run end-to-end NBA Spatial Efficiency ETL Pipeline."""
    setup_logging()
    logger = logging.getLogger("ETL_Pipeline")

    logger.info("==================================================")
    logger.info("STARTING NBA SPATIAL EFFICIENCY & EV ETL PIPELINE")
    logger.info("==================================================")

    try:
        # Step 1: Ingestion
        logger.info("--- Step 1: Raw Shot Data Ingestion ---")
        df_raw = ingest_raw_shots(force_refresh=force_refresh)

        # Step 2: Processing & Spatial Math
        logger.info("--- Step 2: Spatial Feature Engineering & EV Modeling ---")
        df_facts = process_spatial_features(df_raw)

        # Step 3: Export Star-Schema Tables
        logger.info("--- Step 3: Exporting Power BI Star-Schema Datasets ---")
        datasets = export_processed_datasets(df_facts)

        logger.info("==================================================")
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("==================================================")
        logger.info(f"Fact Shots Processed: {len(datasets['fact_shots'])} records")
        logger.info(f"Dim Players Processed: {len(datasets['dim_player'])} records")
        logger.info(f"Dim Shot Zones Processed: {len(datasets['dim_shot_zone'])} zones")

    except Exception as e:
        logger.critical(f"Pipeline execution failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NBA Spatial Efficiency & EV Pipeline CLI")
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Bypass local cache and query NBA Stats API directly."
    )
    args = parser.parse_args()
    run_etl_pipeline(force_refresh=args.force_refresh)
