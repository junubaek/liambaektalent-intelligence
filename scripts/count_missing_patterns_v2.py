import os
import json
import urllib.request
import urllib.error

def count_empty_patterns():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    token = secrets["NOTION_API_KEY"]
    db_id = secrets["NOTION_DATABASE_ID"]
    
    has_more = True
    next_cursor = None
    empty_count = 0
    
    while has_more:
        payload = {
            "filter": {
                "property": "Functional Patterns",
                "multi_select": {
                    "is_empty": True
                }
            },
            "page_size": 100
        }
        if next_cursor:
            payload["start_cursor"] = next_cursor

        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{db_id}/query", 
            data=json.dumps(payload).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                empty_count += len(res.get("results", []))
                has_more = res.get("has_more", False)
                next_cursor = res.get("next_cursor")
        except Exception as e:
            print(f"Error: {e}")
            break
            
    print(f"\nTotal candidates with EMPTY Functional Patterns: {empty_count}")

if __name__ == "__main__":
    count_empty_patterns()
