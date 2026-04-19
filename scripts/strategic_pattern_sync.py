import os
import json
import sqlite3
import requests
import time
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from headhunting_engine.normalization.pattern_merger import PatternMerger

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
DATABASE_ID = "31a22567-1b6f-8177-86da-ff626bb1e66c"
DB_PATH = "c:/Users/cazam/Downloads/안티그래비티/headhunting_engine/data/analytics.db"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def strategic_sync():
    print("🎯 Starting Strategic Pattern Merging Sync (v6.3.6)...")
    merger = PatternMerger()
    
    # 1. Fetch Candidates from SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT notion_id, data_json FROM candidate_snapshots WHERE notion_id IS NOT NULL")
    rows = cursor.fetchall()
    
    print(f"🔍 Processing {len(rows)} candidates for strategic merging...")

    count = 0
    t0 = time.time()
    for notion_id, data_json in rows:
        try:
            req_start = time.time()
            data = json.loads(data_json)
            raw_patterns = [p.get("pattern", "") for p in data.get("patterns", [])]
            
            # Use the new merger
            consolidated = merger.merge_list(raw_patterns, limit=7)
            notion_patterns = [{"name": p[:100]} for p in consolidated]
            
            payload = {
                "properties": {
                    "Experience Patterns": {"multi_select": notion_patterns}
                }
            }
            
            patch_resp = requests.patch(f"https://api.notion.com/v1/pages/{notion_id}", headers=HEADERS, json=payload, timeout=10)
            req_duration = time.time() - req_start
            
            if patch_resp.status_code == 200:
                count += 1
                if count % 10 == 0:
                    avg_speed = (time.time() - t0) / count
                    print(f"✅ [{count}/{len(rows)}] Merged tags for {notion_id} ({req_duration:.2f}s). Avg: {avg_speed:.2f}s/page")
            else:
                print(f"⚠️ Failed to update page {notion_id}: {patch_resp.status_code}")
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error processing {notion_id}: {e}")

    print(f"🏁 Strategic Sync Complete. {count} pages refined.")
    conn.close()

if __name__ == "__main__":
    strategic_sync()
