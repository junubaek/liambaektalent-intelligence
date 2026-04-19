import json, requests

with open("secrets.json") as f:
    key = json.load(f)["NOTION_API_KEY"]

headers = {
    "Authorization": f"Bearer {key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

db_ids = {
    "우아한형제들": "da72c770-5f3a-4d31-b93f-7c3891e741e8",
    "카카오페이증권": "3da58658-96f2-487c-9870-30e5a7bd5d49",
    "인플루엔셜": "f1081b6e-e505-491d-b365-a49dda7de99c"
}

for name, db_id in db_ids.items():
    print(f"--- {name} JD DB ---")
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    try:
        res = requests.post(url, headers=headers).json()
        if "results" not in res:
            print("Error from API:", res)
            continue
        count = 0
        for page in res.get("results", []):
            props = page.get("properties", {})
            title_text = ""
            desc = ""
            for k, v in props.items():
                if v["type"] == "title" and v["title"]:
                    title_text = ''.join(x['plain_text'] for x in v['title'])
                elif v["type"] == "rich_text" and v["rich_text"]:
                    desc += "".join(r["plain_text"] for r in v["rich_text"]) + " "
                elif v["type"] == "multi_select":
                    desc += ",".join(opt["name"] for opt in v["multi_select"]) + " "
            if title_text or desc:
                print(f"[{title_text}] {desc}")
                count += 1
        if count == 0:
            print("No JDs found or no readable fields.")
    except Exception as e:
        print(f"Error: {e}")
