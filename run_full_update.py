import logging
import json
import os
from sync_coordinator import SyncCoordinator
from data_curator import DataCurator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import requests

def reload_index():
    logger.info("Attempting to signal backend to reload REVERSE_INDEX...")
    try:
        res = requests.post("http://localhost:8000/api/reload-synonyms", timeout=5)
        if res.status_code == 200:
            data = res.json()
            logger.info(f"Backend hot-reload successful. Loaded {data.get('total_keywords')} keywords.")
        else:
            logger.warning(f"Backend hot-reload non-200 response: {res.status_code}")
    except Exception as api_e:
        logger.warning(f"Could not reach backend for hot-reload. Ensure backend is running. Error: {api_e}")

def main():
    logger.info("Starting Full Initial Update Cycle (Sync -> Curate -> Ontology)...")
    
    try:
        # 1. Sync
        logger.info("[Step 1] Running Sync Coordinator...")
        sync = SyncCoordinator()
        sync_count = sync.sync_recent_changes()
        logger.info(f"Sync complete. Synchronized {sync_count} records.")
        
        # 2. Curate & Ontology
        logger.info("[Step 2 & 3] Running Data Curator & Keyword Ontologist...")
        curator = DataCurator()
        # For initial run, process up to 200 candidates needing attention
        repaired_count = curator.run_clean_cycle(limit=200)
        
        # 3. Finalize
        reload_index()
        logger.info(f"Full Initial Update Complete! Repaired/Updated Candidate Count: {repaired_count}")
        
    except Exception as e:
        logger.error(f"Full update failed: {e}")

if __name__ == "__main__":
    main()
