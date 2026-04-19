import json, requests

with open("secrets.json") as f:
    key = json.load(f)["NOTION_API_KEY"]
    db_id = json.load(open("secrets.json"))["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

url = f"https://api.notion.com/v1/databases/{db_id}"
res = requests.get(url, headers=headers).json()

# Dump the properties map
with open("tmp_schema.json", "w", encoding="utf-8") as f:
    json.dump(res.get("properties", {}), f, ensure_ascii=False, indent=2)

print("Schema saved to tmp_schema.json")
