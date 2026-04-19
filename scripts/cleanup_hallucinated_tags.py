import json
import sqlite3
import requests
import time
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.getcwd())
from headhunting_engine.normalization.pattern_merger import PatternMerger

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
DATABASE_ID = "31a22567-1b6f-8177-86da-ff626bb1e66c"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def cleanup_hallucinations():
    print("🧹 Starting Placeholder Pattern Cleanup (v6.3.8)...")
    merger = PatternMerger()
    
    # 1. Query Notion for pages containing the bad tag
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    filter_payload = {
        "filter": {
            "property": "Experience Patterns",
            "multi_select": {
                "contains": "Standardized_Functional_Pattern"
            }
        }
    }
    
    resp = requests.post(url, headers=HEADERS, json=filter_payload).json()
    pages = resp.get('results', [])
    print(f"🔍 Found {len(pages)} pages with hallucinated tags.")

    for page in pages:
        pid = page['id']
        name = "Unknown"
        props = page.get('properties', {})
        
        # Get Name
        title_prop = props.get('이름', {}).get('title', [])
        if title_prop:
            name = title_prop[0].get('plain_text', 'Unknown')
        
        # Current Patterns
        current_patterns = props.get('Experience Patterns', {}).get('multi_select', [])
        new_patterns = [p for p in current_patterns if p['name'] != "Standardized_Functional_Pattern"]
        
        # [Strategy] If removing leaves it empty, we should ideally re-inject the raw patterns if possible.
        # For now, just removing the "Gunk".
        
        update_payload = {
            "properties": {
                "Experience Patterns": {"multi_select": new_patterns}
            }
        }
        
        patch_resp = requests.patch(f"https://api.notion.com/v1/pages/{pid}", headers=HEADERS, json=update_payload)
        if patch_resp.status_code == 200:
            print(f"✅ Cleaned {name}")
        else:
            print(f"⚠️ Failed to clean {name}: {patch_resp.text}")
        
        time.sleep(0.3)

if __name__ == "__main__":
    cleanup_hallucinations()
