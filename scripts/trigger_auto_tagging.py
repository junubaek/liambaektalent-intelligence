import sqlite3
import json
import os
import sys
import time

# Add root to sys.path
sys.path.append(os.getcwd())
from connectors.notion_api import NotionClient
from headhunting_engine.normalization.pattern_merger import PatternMerger

# Configuration
DB_PATH = "headhunting_engine/data/analytics.db"
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
nc = NotionClient(NOTION_TOKEN)
merger = PatternMerger()

def trigger_auto_tagging(pattern_name, sector):
    """
    v6.3.6: Reciprocal Intelligence Loop with Strategic Merging
    Scans the candidate pool for a specific pattern name (promoted from JD discovery)
    and updates existing candidates if matched in raw_text.
    """
    print(f"🚀 Triggering Auto-Tagging for Pattern: {pattern_name} (Sector: {sector})")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Fetch candidates from the relevant sector
    cursor.execute("SELECT id, name, data_json, notion_id FROM candidate_snapshots WHERE data_json LIKE ?", (f'%{sector}%',))
    candidates = cursor.fetchall()
    
    print(f"🔍 Scanning {len(candidates)} candidates in sector {sector}...")
    
    match_count = 0
    pattern_keyword = pattern_name.replace("__TEMP__", "").replace("_", " ").lower()

    for rid, name, djson, nid in candidates:
        try:
            data = json.loads(djson)
            raw_text = data.get("raw_text", "").lower()
            
            if pattern_keyword in raw_text:
                print(f"  ✨ Match found for {name}!")
                
                # Check if pattern already exists
                existing_patterns = [p["pattern"] for p in data.get("patterns", [])]
                if pattern_name not in existing_patterns:
                    # 3. Local DB Update
                    data["patterns"].append({
                        "pattern": pattern_name,
                        "depth": "Mentioned",
                        "impact": "Auto-tagged from JD Discovery Loop"
                    })
                    cursor.execute("UPDATE candidate_snapshots SET data_json = ? WHERE id = ?", (json.dumps(data), rid))
                    
                    # 4. Strategic Merging & Notion Update (Multi-select v6.3.6)
                    if nid:
                        current_patterns = [p["pattern"] for p in data.get("patterns", [])]
                        merged_patterns = merger.merge_list(current_patterns, limit=7)
                        notion_patterns = [{"name": p} for p in merged_patterns]
                        
                        nc.update_page_properties(nid, {
                            "Experience Patterns": {"multi_select": notion_patterns}
                        })
                        print(f"  ✅ Updated Notion Page (Strategic) for {name}")
                    
                    match_count += 1
                    conn.commit()
                    time.sleep(0.3) # Notion rate limit
        except Exception as e:
            print(f"  ❌ Error tagging {name}: {e}")

    conn.close()
    print(f"✨ Auto-Tagging Complete. Matched {match_count} candidates.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/trigger_auto_tagging.py <pattern_name> <sector>")
    else:
        trigger_auto_tagging(sys.argv[1], sys.argv[2])
