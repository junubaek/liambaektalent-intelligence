import json
import urllib.request

def test_update():
    with open('secrets.json', 'r') as f:
        env = json.load(f)

    token = env.get("NOTION_API_KEY")
    db_id = env.get("NOTION_DATABASE_ID")

    if not token or not db_id:
        print("Missing credentials")
        return

    # First fetch ONE candidate
    url_query = f"https://api.notion.com/v1/databases/{db_id}/query"
    req_query = urllib.request.Request(
        url_query,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        },
        method="POST",
        data=json.dumps({"page_size": 1}).encode("utf-8")
    )

    try:
        with urllib.request.urlopen(req_query) as res:
            data = json.loads(res.read().decode())
            if not data.get("results"):
                print("No candidates found")
                return
            
            page_id = data["results"][0]["id"]
            name_prop = data["results"][0]["properties"].get("Name", {}).get("title", [])
            name = name_prop[0]["plain_text"] if name_prop else "Unknown"
            
            print(f"Target selected: {name} ({page_id})")

            # Try updating with a dummy test pattern
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            payload = {
                "properties": {
                    "Functional Patterns": {
                        "multi_select": [{"name": "Test Pattern Update"}]
                    }
                }
            }
            
            req_update = urllib.request.Request(
                update_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                },
                method="PATCH",
                data=json.dumps(payload).encode("utf-8")
            )
            
            try:
                with urllib.request.urlopen(req_update) as up_res:
                    print(f"Update Success! Status: {up_res.status}")
            except urllib.error.HTTPError as he:
                print(f"Update Failed. HTTP {he.code}: {he.read().decode('utf-8')}")

    except Exception as e:
        print(f"Fetch failed: {e}")

if __name__ == "__main__":
    test_update()
