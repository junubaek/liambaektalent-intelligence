import json
import urllib.request
import urllib.error

with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
DATABASE_ID = secrets["NOTION_DATABASE_ID"]

def get_database_schema():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        print(f"Error: {e.read().decode('utf-8')}")
        return {}

schema = get_database_schema()
patterns_prop = schema.get("properties", {}).get("Functional Patterns", {})
options = patterns_prop.get("multi_select", {}).get("options", [])
patterns = [opt["name"] for opt in options]

with open("current_patterns.json", "w", encoding="utf-8") as f:
    json.dump(patterns, f, ensure_ascii=False, indent=2)

print(f"Found {len(patterns)} patterns.")
