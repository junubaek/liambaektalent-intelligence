import json
import requests
import os

with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
DATABASE_ID = secrets["NOTION_DATABASE_ID"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_500():
    print("Fetching up to 500 candidates from Notion...")
    results = []
    has_more = True
    next_cursor = None
    
    while has_more and len(results) < 500:
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        r = requests.post(url, headers=HEADERS, json=payload)
        if r.status_code != 200:
            print(f"Error fetching data: {r.status_code} {r.text}")
            break
            
        data = r.json()
        results.extend(data.get("results", []))
        
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)
        print(f"Fetched {len(results)} so far...")
        
    final_output = {"results": results[:500]}
    
    with open("temp_500_candidates.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(final_output['results'])} items to temp_500_candidates.json")

if __name__ == "__main__":
    fetch_500()
