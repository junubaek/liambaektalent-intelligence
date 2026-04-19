import time
import logging
import schedule
import requests
from sync_coordinator import SyncCoordinator
from data_curator import DataCurator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def automated_hourly_job():
    logger.info("--- [Automated Hourly Cycle] Starting Sync and Curation ---")
    try:
        # Step 1: Sync new or changed Notion records
        sync = SyncCoordinator()
        sync_count = sync.sync_recent_changes()
        logger.info(f"Sync complete. Synchronized {sync_count} records.")
        
        # Step 2 & 3: Run AI Curator (which internally calls Keyword Ontologist)
        curator = DataCurator()
        # Processing up to 100 pages every hour.
        repaired_count = curator.run_clean_cycle(limit=100)
        
        logger.info(f"--- [Automated Hourly Cycle] Complete. Repaired/Updated Candidate Count: {repaired_count} ---")
        
        # Step 4: Hot-Reload Backend Keywords
        try:
            res = requests.post("http://localhost:8000/api/reload-synonyms", timeout=5)
            if res.status_code == 200:
                data = res.json()
                logger.info(f"Backend hot-reload successful. Loaded {data.get('total_keywords')} keywords.")
            else:
                logger.warning(f"Backend hot-reload non-200 response: {res.status_code}")
        except Exception as api_e:
            logger.warning(f"Could not reach backend for hot-reload. Ensure backend is running. Error: {api_e}")

    except Exception as e:
        logger.error(f"Error during hourly automated cycle: {e}")

# Register the job to run every 1 hour
schedule.every(1).hours.do(automated_hourly_job)

if __name__ == "__main__":
    logger.info("Initializing 1-Hour Automated Background Scheduler (Antigravity v5.0)...")
    logger.info("The scheduler will wake up every 1 hour to sync Notion, evolve the Keyword Ontology, and trigger hot-reload.")
    
    # Run the main loop
    while True:
        schedule.run_pending()
        time.sleep(60) # Sleep for a minute before checking schedule again
