import json
from notion_client import Client

with open('secrets.json', 'r') as f:
    key = json.load(f)['notion_api_key']
notion = Client(auth=key)

res = notion.search(filter={'value': 'database', 'property': 'object'})
for d in res['results']:
    title = d.get('title', [])
    if title:
        name = title[0]['plain_text']
        print(f"DB: {name} | ID: {d['id']}")
