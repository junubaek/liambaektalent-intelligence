import requests
import json
import time

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)
token = secrets["NOTION_API_KEY"]
db_id = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_live_pages():
    print("📋 Fetching all live pages from Notion...")
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    pages = []
    has_more = True
    start_cursor = None
    
    while has_more:
        payload = {"page_size": 100}
        if start_cursor: payload["start_cursor"] = start_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        results = resp.get('results', [])
        for r in results:
            if not r.get('archived'):
                pages.append(r)
        has_more = resp.get('has_more', False)
        start_cursor = resp.get('next_cursor')
        print(f"  -> Loaded {len(pages)} live pages...")
    return pages

def jaccard_similarity(set1, set2):
    if not set1 and not set2: return 1.0
    if not set1 or not set2: return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def run_intelligent_dedupe():
    pages = get_live_pages()
    name_groups = {}
    
    for p in pages:
        props = p['properties']
        title_list = props.get('이름', {}).get('title', [])
        if not title_list: continue
        name = title_list[0].get('plain_text')
        
        if name not in name_groups:
            name_groups[name] = []
        
        patterns = set([pt["name"] for pt in props.get('Experience Patterns', {}).get('multi_select', [])])
        summary = "".join([t["plain_text"] for t in props.get("경력 Summary", {}).get("rich_text", [])])
        sector = [s["name"] for s in props.get('Primary Sector', {}).get('multi_select', [])]
        
        name_groups[name].append({
            "id": p['id'],
            "patterns": patterns,
            "summary": summary,
            "sector": sector,
            "score": props.get('v6.2 Score', {}).get('number', 0) or 0,
            "has_link": 1 if props.get('구글드라이브 링크', {}).get('url') else 0
        })

    archived_count = 0
    preserved_namesakes = 0
    
    print("\n🧐 Analyzing duplicates and namesakes...")
    for name, group in name_groups.items():
        if len(group) <= 1: continue
        
        # Sort group by quality: links > score > patterns > summary length
        group.sort(key=lambda x: (x['has_link'], x['score'], len(x['patterns']), len(x['summary'])), reverse=True)
        
        to_keep = [group[0]]
        
        for i in range(1, len(group)):
            current = group[i]
            is_duplicate = False
            
            for kept in to_keep:
                # Compare similarity
                sim_patterns = jaccard_similarity(current['patterns'], kept['patterns'])
                
                # Check summary similarity (simple overlap check)
                common_keywords = set(current['summary'].split()).intersection(set(kept['summary'].split()))
                sim_summary = len(common_keywords) / max(len(current['summary'].split()), 1)
                
                # Decision logic:
                # If sector matches AND (patterns are similar OR summary is similar)
                # It's highly likely the same person.
                if current['sector'] == kept['sector'] and (sim_patterns > 0.5 or sim_summary > 0.3):
                    is_duplicate = True
                    break
                
            if is_duplicate:
                # Archive the lower quality duplicate
                print(f"🗑️ Archiving redundant duplicate: {name} (ID: {current['id']})")
                requests.patch(f"https://api.notion.com/v1/pages/{current['id']}", headers=headers, json={"archived": True})
                archived_count += 1
            else:
                # This is a namesake (동명이인) - Keep it!
                print(f"🌟 Preserving namesake: {name} (ID: {current['id']})")
                to_keep.append(current)
                preserved_namesakes += 1
        
        time.sleep(0.1) # Small delay for API

    print(f"\n✅ CLEANUP COMPLETE:")
    print(f"  - Total Archived: {archived_count}")
    print(f"  - Namesakes Preserved: {preserved_namesakes}")

if __name__ == "__main__":
    run_intelligent_dedupe()
