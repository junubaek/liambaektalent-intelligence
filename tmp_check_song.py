import json
import os

with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for c in data:
    name = c.get('name') or c.get('이름') or ''
    if '송선욱' in name:
        print(f"Name: {name}")
        print(f"ID: {c.get('id')}")
        print(f"URL: {c.get('url')}")
        print(f"File URL: {c.get('file_url') or c.get('Resume Link')}")
        print("-" * 40)
