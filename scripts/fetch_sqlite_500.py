import sqlite3
import json

DB_PATH = "c:/Users/cazam/Downloads/안티그래비티/headhunting_engine/data/analytics.db"

def fetch_local():
    print(f"Connecting to local SQLite DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract only valid JSON payloads that correspond to candidate items
    cursor.execute("SELECT data_json FROM candidate_snapshots WHERE data_json IS NOT NULL")
    rows = cursor.fetchall()
    
    results = []
    for (data_json,) in rows:
        try:
            data = json.loads(data_json)
            # data could be in different formats depending on how it was saved
            # Usually it's the raw Notion API response for the page
            results.append(data)
            if len(results) >= 500:
                break
        except Exception:
            pass
            
    final_output = {"results": results}
    with open("temp_500_candidates.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(results)} items from local DB to temp_500_candidates.json")
    conn.close()

if __name__ == "__main__":
    fetch_local()
