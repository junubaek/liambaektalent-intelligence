import json
import urllib.request
import math

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

NOTION_API_KEY = secrets["NOTION_API_KEY"].strip()
NOTION_DATABASE_ID = secrets["NOTION_DATABASE_ID"].strip()

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

payload = {
    "filter": {
        "property": "Functional Patterns",
        "multi_select": {
            "is_empty": True
        }
    }
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        
        # We might not get all, but we can check if there's 'has_more'. 
        # Actually, query just brings up to 100. Let's paginate to get the true total count.
        total_missing = len(result.get('results', []))
        has_more = result.get('has_more', False)
        next_cursor = result.get('next_cursor')
        
        while has_more:
            payload["start_cursor"] = next_cursor
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                total_missing += len(res.get('results', []))
                has_more = res.get('has_more', False)
                next_cursor = res.get('next_cursor')

        print(f"Total True Missing: {total_missing}")
        if total_missing > 0:
            estimated_hours = (total_missing / 100) * 0.7  # 100 candidates take ~40 mins
            print(f"Estimated time remaining: {estimated_hours:.1f} hours")
        else:
            print(f"Estimated time remaining: 0 hours")

except Exception as e:
    print(f"Error: {e}")
