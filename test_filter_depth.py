import json
import requests

try:
    with open("secrets.json", "r") as f:
        _secrets = json.load(f)
    notion_token = _secrets.get("NOTION_API_KEY", "")
    db_id = _secrets.get("NOTION_DATABASE_ID", "")
    
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Generate 105 simple dummy OR conditions
    dummy_ors = [{"property": "이름", "title": {"contains": f"TEST_{i}"}} for i in range(105)]
    
    # Try flat OR
    flat_payload = {
        "filter": {"and": [{"or": dummy_ors}]},
        "page_size": 1
    }
    r = requests.post(url, headers=headers, json=flat_payload)
    print("Flat OR status:", r.status_code)
    
    # Try chunked nested OR
    chunked_ors = []
    for i in range(0, len(dummy_ors), 50):
        chunked_ors.append({"or": dummy_ors[i:i+50]})
        
    nested_payload = {
        "filter": {"and": [{"or": chunked_ors}]},
        "page_size": 1
    }
    r2 = requests.post(url, headers=headers, json=nested_payload)
    print("Nested OR status:", r2.status_code)
    if r2.status_code != 200:
        print("Nested OR error:", r2.text)

except Exception as e:
    print(e)
