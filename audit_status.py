import json
import requests
import time

def audit():
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    
    NOTION_API_KEY = secrets['NOTION_API_KEY']
    DATABASE_ID = secrets['NOTION_DATABASE_ID']
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # Check for live candidates with missing patterns
    missing_patterns_filter = {
        "and": [
            {
                "property": "Status",
                "select": {
                    "equals": "Live"
                }
            },
            {
                "property": "Experience Patterns",
                "rich_text": {
                    "is_empty": True
                }
            }
        ]
    }
    
    total_missing = 0
    has_more = True
    next_cursor = None
    
    while has_more:
        payload = {"filter": missing_patterns_filter, "page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        total_missing += len(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
        print(f"Counted {total_missing} so far...")
    
    print(f"\nFINAL AUDIT RESULTS:")
    print(f"Total Live Candidates missing Experience Patterns: {total_missing}")

if __name__ == "__main__":
    audit()
