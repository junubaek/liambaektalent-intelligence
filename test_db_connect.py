import json
import os
from notion_client import Client

try:
    with open("secrets.json", "r") as f:
        _secrets = json.load(f)
except FileNotFoundError:
    _secrets = {}

NOTION_TOKEN = _secrets.get("NOTION_API_KEY", "")
NOTION_DB_ID = _secrets.get("NOTION_DATABASE_ID", "")

print(f"Token present: {bool(NOTION_TOKEN)}")
print(f"DB ID present: {bool(NOTION_DB_ID)}")

if not NOTION_TOKEN or not NOTION_DB_ID:
    print("Missing credentials!")
    exit(1)

client = Client(auth=NOTION_TOKEN)

try:
    response = client.request(
        path=f"databases/{NOTION_DB_ID}/query",
        method="POST",
        body={"page_size": 1}
    )
    print("API SUCCESS: DB Connected.")
    results = response.get("results", [])
    print(f"Found pages in DB: {len(results)}")
    
    if results:
        props = results[0].get("properties", {})
        names = props.get("이름", {}).get("title", [])
        name_val = "".join([n.get("plain_text", "") for n in names]) if names else "Unknown"
        print(f"Sample Candidate Name: {name_val}")
        
except Exception as e:
    print(f"API FAIL: {e}")
