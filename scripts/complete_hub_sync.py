import os
import json
import sqlite3
import requests
import time
import sys

# Add parent directory to sys.path for merger import
sys.path.append(os.getcwd())
from headhunting_engine.normalization.pattern_merger import PatternMerger

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
DATABASE_ID = "31a22567-1b6f-8177-86da-ff626bb1e66c"
DB_PATH = "headhunting_engine/data/analytics.db"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_complete_sync():
    print("🚀 Starting Complete Notion Sync (v6.3.7)...")
    merger = PatternMerger()
    
    # 1. Fetch Candidates from SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Check if notion_id is not null
    cursor.execute("SELECT notion_id, data_json, name FROM candidate_snapshots WHERE notion_id IS NOT NULL")
    rows = cursor.fetchall()
    
    print(f"🔍 Found {len(rows)} candidates to finalize. Starting update loop...")

    count = 0
    t0 = time.time()
    for notion_id, data_json, name in rows:
        try:
            req_start = time.time()
            data = json.loads(data_json)
            
            # Extract Components
            # 1. Experience Patterns (Merged)
            raw_patterns = [p.get("pattern", "") for p in data.get("patterns", [])]
            consolidated = merger.merge_list(raw_patterns, limit=7)
            notion_patterns = [{"name": p[:100]} for p in consolidated]
            
            # 2. Experience Summary
            profile = data.get("candidate_profile", {})
            summary = profile.get("experience_summary", "")
            if not summary and "summary" in data:
                summary = data["summary"]
            
            # 3. GDrive Link
            gdrive_link = data.get("gdrive_link", profile.get("gdrive_link", ""))
            
            # Build Metadata Update
            properties = {
                "Experience Patterns": {"multi_select": notion_patterns}
            }
            
            if summary:
                properties["경력 Summary"] = {"rich_text": [{"text": {"content": summary[:2000]}}]}
            
            if gdrive_link:
                properties["구글드라이브 링크"] = {"url": gdrive_link}
            
            payload = {"properties": properties}
            
            patch_resp = requests.patch(f"https://api.notion.com/v1/pages/{notion_id}", headers=HEADERS, json=payload, timeout=12)
            req_duration = time.time() - req_start
            
            if patch_resp.status_code == 200:
                count += 1
                if count % 10 == 0:
                    avg_speed = (time.time() - t0) / count
                    print(f"✅ [{count}/{len(rows)}] Finalized {name} ({req_duration:.2f}s). Avg: {avg_speed:.2f}s/page")
            else:
                # If 400, output details
                if patch_resp.status_code == 400:
                    print(f"⚠️ Validation Error for {name}: {patch_resp.text}")
                else:
                    print(f"⚠️ Failed {name} ({patch_resp.status_code})")
            
            # Notion Rate Limit Safety (v3 API standard is 3 req/sec)
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ Error processing {name}: {e}")

    print(f"🏁 Complete Sync Finished. {count} candidates finalized in Notion Hub.")
    conn.close()

if __name__ == "__main__":
    get_complete_sync()
