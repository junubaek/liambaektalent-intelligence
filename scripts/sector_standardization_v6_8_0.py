import json
import requests
import time

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

STANDARD_SECTORS = {
    "TECH_SW", "TECH_HW", "SEMICONDUCTOR", "DATA_AI", 
    "PRODUCT", "BUSINESS", "SECURITY", "CORPORATE", "CREATIVE"
}

MAPPING_RULES = {
    "CLOUD": "TECH_SW",
    "LOGISTICS": "BUSINESS",
    "FINANCIAL": "BUSINESS",
    "Insufficient_Data": "Unclassified",
    "Unclassified": "Unclassified"
}

def clean_sector_tags(raw_tags):
    """
    Cleans and standardizes sector tags.
    Input: List of tag names from Notion
    Output: Set of standardized tag names
    """
    clean_set = set()
    for tag in raw_tags:
        # 1. Split by pipe if exists
        parts = [p.strip() for p in tag.split("|")]
        for p in parts:
            # 2. Check if it's already standard
            if p in STANDARD_SECTORS:
                clean_set.add(p)
            # 3. Check mapping rules
            elif p in MAPPING_RULES:
                mapped = MAPPING_RULES[p]
                if mapped != "Unclassified":
                    clean_set.add(mapped)
            # 4. Handle edge cases (noise)
            elif "Pick one" in p:
                continue
            else:
                # If unknown, map to Unclassified for now
                pass
    
    if not clean_set:
        return {"Unclassified"}
    return clean_set

def run_standardization():
    print("🚀 Starting Primary Sector Standardization (v6.8.0)...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    has_more = True
    next_cursor = None
    processed = 0
    updated = 0
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        
        for p in resp.get('results', []):
            if p.get('archived'): continue
            processed += 1
            nid = p['id']
            props = p['properties']
            current_tags = [s['name'] for s in props.get('Primary Sector', {}).get('multi_select', [])]
            
            # Decide if cleanup is needed
            # 1. Any tag has "|"
            # 2. Any tag is not in STANDARD_SECTORS
            needs_update = False
            for t in current_tags:
                if "|" in t or t not in STANDARD_SECTORS:
                    needs_update = True
                    break
            
            if needs_update:
                new_tags_set = clean_sector_tags(current_tags)
                new_multi_select = [{"name": t} for t in sorted(list(new_tags_set))]
                
                print(f"  [Update] {nid}: {current_tags} -> {list(new_tags_set)}")
                requests.patch(f"https://api.notion.com/v1/pages/{nid}", headers=headers, json={
                    "properties": {
                        "Primary Sector": {"multi_select": new_multi_select}
                    }
                })
                updated += 1
                time.sleep(0.5) # Avoid rate limits
                
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')
        print(f"  Processed {processed} pages... (Updated: {updated})")

    print(f"\n✨ Standardization Complete. Total Updated: {updated}")

if __name__ == "__main__":
    run_standardization()
