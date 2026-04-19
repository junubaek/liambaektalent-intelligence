import os
import json
import sqlite3
import requests
import time

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

def consolidate_pattern(name):
    """v6.3.5 Smart Consolidation Mapping"""
    name = (name or "").lower().strip()
    if not name: return None

    # 1. Soft Skill & Attitude Blacklist
    blacklist = ["communication", "teamwork", "passion", "sincerity", "collaboration", "problem solving", "leadership and development"]
    if any(b in name for b in blacklist):
        return "Leadership_HRM" if "leadership" in name else None
    
    # 2. Semantic Consolidation (High-frequency clusters from DB analysis)
    mappings = {
        "frontend": "Frontend_Development", "react": "Frontend_Development", "vue": "Frontend_Development",
        "backend": "Backend_Development", "java": "Backend_Development", "python": "Backend_Development", "spring": "Backend_Development",
        "mobile": "Mobile_App_Development", "ios": "Mobile_App_Development", "android": "Mobile_App_Development",
        "data analysis": "Product_Analytics", "sql": "Product_Analytics", "tableau": "Product_Analytics",
        "recruitment": "Recruitment_Strategy", "hiring": "Recruitment_Strategy",
        "strategic planning": "Corporate_Strategy", "business development": "Business_Strategy"
    }
    for key, val in mappings.items():
        if key in name: return val
    
    return name.title().replace(" ", "_")

def fast_sync():
    print("🚀 Starting Fast Pattern Sync (v6.3.5)...")
    
    # 1. Revert Database Schema to Multi-select
    print("🛠️ Reverting 'Experience Patterns' to Multi-select...")
    schema_payload = {
        "properties": {
            "Experience Patterns": {"multi_select": {}}
        }
    }
    resp = requests.patch(f"https://api.notion.com/v1/databases/{DATABASE_ID}", headers=HEADERS, json=schema_payload)
    if resp.status_code != 200:
        print(f"❌ Schema update failed: {resp.text}")
        return

    # 2. Fetch Candidates from SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT notion_id, data_json FROM candidate_snapshots WHERE notion_id IS NOT NULL")
    rows = cursor.fetchall()
    
    print(f"🔍 Found {len(rows)} candidates with Notion IDs. Syncing patterns...")

    count = 0
    t0 = time.time()
    for notion_id, data_json in rows:
        try:
            req_start = time.time()
            data = json.loads(data_json)
            raw_patterns = [p.get("pattern", "") for p in data.get("patterns", [])]
            
            consolidated = []
            for rp in raw_patterns:
                cp = consolidate_pattern(rp)
                if cp and cp not in consolidated:
                    consolidated.append(cp)
            
            notion_patterns = [{"name": p[:100]} for p in consolidated[:7]]
            
            payload = {
                "properties": {
                    "Experience Patterns": {"multi_select": notion_patterns}
                }
            }
            
            patch_resp = requests.patch(f"https://api.notion.com/v1/pages/{notion_id}", headers=HEADERS, json=payload, timeout=10)
            req_duration = time.time() - req_start
            
            if patch_resp.status_code == 200:
                count += 1
                if count % 5 == 0:
                    avg_speed = (time.time() - t0) / count
                    print(f"✅ [{count}/{len(rows)}] Updated {notion_id} ({req_duration:.2f}s). Avg: {avg_speed:.2f}s/page")
            else:
                print(f"⚠️ Failed to update page {notion_id} ({patch_resp.status_code}): {patch_resp.text}")
            
            time.sleep(0.1)  # Faster sleep
            
        except Exception as e:
            print(f"❌ Error processing {notion_id}: {e}")

    print(f"🏁 Fast Sync Complete. {count} pages updated.")
    conn.close()

if __name__ == "__main__":
    fast_sync()
