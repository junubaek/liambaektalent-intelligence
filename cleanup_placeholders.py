import json
import time
from datetime import datetime, timedelta
from connectors.notion_api import HeadhunterDB

def main():
    print("Cleaning up placeholder Notion pages...")
    db = HeadhunterDB()
    client = db.client
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
            db_id = secrets.get("NOTION_DATABASE_ID")
    except Exception:
        db_id = client.search_db_by_name("Vector DB")
    if not db_id:
        print("DB not found")
        return
        
    print(f"Querying DB {db_id}...")
    res = client.query_database(db_id, limit=None)
    all_results = res.get('results', [])
    
    print(f"Total pages: {len(all_results)}")
    
    # Calculate time 1 hour ago
    time_threshold = datetime.utcnow() - timedelta(hours=1)
    
    count = 0
    for p in all_results:
        created_time_str = p.get('created_time')
        if not created_time_str:
            continue
            
        # Parse created_time "2026-03-25T03:32:00.000Z"
        try:
            created_time = datetime.strptime(created_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            created_time = datetime.strptime(created_time_str, "%Y-%m-%dT%H:%M:%SZ")

        if created_time > time_threshold:
            # This was created very recently (during our test)
            page_id = p['id']
            
            # Additional check: we can fetch the full text to be sure, or just delete it if the title is one of the "JY_" ones.
            # Actually, to be very safe, let's fetch full text and see if it contains "Original File Content Not Extracted"
            text = client.get_page_full_text(page_id)
            if "Original File Content Not Extracted" in text:
                print(f"Archiving placeholder page: {page_id}")
                client.archive_page(page_id)
                count += 1
                time.sleep(0.2)
                
    print(f"Cleaned up {count} placeholder pages.")

if __name__ == '__main__':
    main()
