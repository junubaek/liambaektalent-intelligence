import json
import requests
import os

try:
    with open("secrets.json", "r") as f:
        _secrets = json.load(f)
except FileNotFoundError:
    _secrets = {}

NOTION_TOKEN = _secrets.get("NOTION_API_KEY", "")
NOTION_DB_ID = _secrets.get("NOTION_DATABASE_ID", "")

url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
data = {
    "page_size": 1
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    results = response.json().get("results", [])
    print(f"RAW HTTP SUCCESS: DB Connected. Found pages: {len(results)}")
else:
    print(f"RAW HTTP FAIL: {response.status_code}")
    print(response.text)
