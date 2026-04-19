import json
import requests
from collections import Counter

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
NOTION_DB_ID = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def audit_sectors():
    print("🔍 Auditing current Primary Sector values in Notion...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    has_more = True
    next_cursor = None
    sector_counts = Counter()
    total_count = 0
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        
        for p in resp.get('results', []):
            if p.get('archived'): continue
            total_count += 1
            props = p['properties']
            sectors = props.get('Primary Sector', {}).get('multi_select', [])
            if not sectors:
                sector_counts["(BLANK)"] += 1
            for s in sectors:
                sector_counts[s['name']] += 1
                
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')
        print(f"  Processed {total_count} pages...")

    print("\n================================")
    print("📊 SECTOR AUDIT REPORT")
    print("================================")
    for sector, count in sector_counts.most_common():
        print(f"- {sector}: {count}")
    print("================================")

if __name__ == "__main__":
    audit_sectors()
