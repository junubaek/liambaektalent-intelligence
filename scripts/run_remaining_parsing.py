import logging
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from data_curator import DataCurator
from sync_coordinator import SyncCoordinator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_all_remaining():
    logger.info("Starting Full Ontology Parsing for all remaining unparsed candidates...")
    
    # 1. First sync any updates from Notion to SQLite just in case
    logger.info("Syncing latest Notion data to SQLite...")
    try:
        sync = SyncCoordinator()
        sync_count = sync.sync_recent_changes()
        logger.info(f"Sync complete. Updated {sync_count} records.")
    except Exception as e:
        logger.warning(f"Sync soft-failed (you can ignore if up to date): {e}")

    # 2. Run DataCurator without tight limit
    # The default for run_clean_cycle if we pass a high limit is to process everything 
    # taking into account rate limits and exceptions.
    logger.info("Starting DataCurator node extraction...")
    curator = DataCurator()
    repaired_count = curator.run_clean_cycle(limit=2000)
    
    logger.info(f"🎉 Finalized Full Parsing Cycle! Newly extracted candidate graphs: {repaired_count}")

if __name__ == "__main__":
    run_all_remaining()
