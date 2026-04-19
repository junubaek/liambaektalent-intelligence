from connectors.notion_api import HeadhunterDB
import json
db = HeadhunterDB()
res = db.client.query_database("1062b3a9-e85d-8012-ba26-d6216db8a005", payload={
    "filter": {"property": "Name", "title": {"contains": "김대중"}}
})
pages = res.get("results", [])
for p in pages:
    props = p.get("properties", {})
    name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "")
    comp = props.get("기존 소속회사", {})
    print(f"Name: {name}, Comp Prop: {comp}")
