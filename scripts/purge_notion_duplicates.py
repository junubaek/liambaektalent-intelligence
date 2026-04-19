import requests
import json
import time

# Configuration
NOTION_DB_ID = "31a22567-1b6f-8177-86da-ff626bb1e66c"

def purge_duplicates():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    token = secrets["NOTION_API_KEY"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    print("🔍 Fetching all pages for deduplication...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    pages = []
    has_more = True
    start_cursor = None
    
    while has_more:
        payload = {"page_size": 100}
        if start_cursor: payload["start_cursor"] = start_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        pages.extend(resp.get('results', []))
        has_more = resp.get('has_more', False)
        start_cursor = resp.get('next_cursor')
        print(f"  -> Loaded {len(pages)} pages...")
    
    # Group by name
    name_map = {}
    for p in pages:
        props = p['properties']
        title_list = props.get('이름', {}).get('title', [])
        if not title_list: continue
        name = title_list[0].get('plain_text', "UNTITLED")
        
        # Heuristic for "best" page: Has Google Drive link or more multi-selects
        has_link = 1 if props.get('구글드라이브 링크', {}).get('url') else 0
        pattern_count = len(props.get('Experience Patterns', {}).get('multi_select', []))
        score = props.get('v6.2 Score', {}).get('number', 0) or 0
        
        # Weighting: Link is most important, then pattern count
        quality_score = (has_link * 100) + (pattern_count * 10) + (score * 0.1)
        
        if name not in name_map:
            name_map[name] = []
        name_map[name].append({
            "id": p['id'],
            "quality": quality_score,
            "created_time": p['created_time']
        })

    total_archived = 0
    print("\n🚀 Starting archival of duplicates...")
    for name, entries in name_map.items():
        if len(entries) > 1:
            # Sort by quality (desc), then created_time (desc)
            sorted_entries = sorted(entries, key=lambda x: (x['quality'], x['created_time']), reverse=True)
            
            # Keep the first one, archive the rest
            best_id = sorted_entries[0]['id']
            to_archive = sorted_entries[1:]
            
            print(f"  [DUP] {name}: keeping {best_id}, archiving {len(to_archive)} others.")
            for entry in to_archive:
                archive_url = f"https://api.notion.com/v1/pages/{entry['id']}"
                requests.patch(archive_url, headers=headers, json={"archived": True})
                total_archived += 1
                time.sleep(0.3) # Avoid rate limits

    print(f"\n✅ Cleanup finished. Total pages archived: {total_archived}")

if __name__ == "__main__":
    purge_duplicates()
