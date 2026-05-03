import json
import requests
import sys

# Set encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Load secrets
with open('secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)

headers = {
    'Authorization': f'Bearer {s["NOTION_API_KEY"]}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

db_id = s.get("NOTION_DISCOVERY_DB_ID", "")
if not db_id:
    print("NOTION_DISCOVERY_DB_ID not found in secrets.json")
    sys.exit(1)

url = f'https://api.notion.com/v1/databases/{db_id}'
r = requests.get(url, headers=headers)
data = r.json()
title = data.get('title', [{}])[0].get('plain_text', 'Unknown')
print(f"Database ID: {db_id}")
print(f"Title: {title}")
