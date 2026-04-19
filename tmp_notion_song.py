import os
import json
from connectors.notion_api import NotionClient

secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.json')
with open(secrets_path, 'r') as f:
    secrets = json.load(f)

client = NotionClient(secrets["NOTION_API_KEY"])
page_id = "33522567-1b6f-8134-8399-dbf4864cc4b6"

page = client.get_page(page_id)
print("--- RAW PAGE PROPERTIES ---")
for key, prop in page["properties"].items():
    prop_type = prop["type"]
    val = None
    if prop_type == "url":
        val = prop["url"]
    elif prop_type == "rich_text":
        val = "".join([t["plain_text"] for t in prop["rich_text"]]) if prop["rich_text"] else ""
    elif prop_type == "title":
        val = "".join([t["plain_text"] for t in prop["title"]]) if prop["title"] else ""
    print(f"[{key}] ({prop_type}): {val}")
