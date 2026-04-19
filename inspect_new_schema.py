import json
from jd_compiler import notion_headers

def inspect():
    import requests
    db_id = "30a22567-1b6f-81c3-9d33-d480330553c0"
    url = f"https://api.notion.com/v1/databases/{db_id}"
    resp = requests.get(url, headers=notion_headers)
    if resp.status_code == 200:
        props = resp.json().get("properties", {})
        print("\\n=== NOTION PROPERTIES ===")
        for k, v in props.items():
            print(f"- {k} [{v['type']}]")
    else:
        print(resp.text)

if __name__ == "__main__":
    inspect()
