import json
from notion_client import Client

with open('secrets.json', 'r') as f:
    key = json.load(f)['NOTION_API_KEY']
notion = Client(auth=key)

db_ids = {
    "우아한형제들": "da72c770-5f3a-4d31-b93f-7c3891e741e8",
    "카카오페이증권": "3da58658-96f2-487c-9870-30e5a7bd5d49",
    "인플루엔셜": "f1081b6e-e505-491d-b365-a49dda7de99c"
}

for name, db_id in db_ids.items():
    print(f"--- {name} JD DB ---")
    try:
        res = notion.databases.query(database_id=db_id)
        for page in res.get('results', []):
            props = page.get('properties', {})
            # Extract plain text from any rich_text or title fields
            title_text = ""
            desc = ""
            for k, v in props.items():
                if v['type'] == 'title' and len(v['title']) > 0:
                    title_text = v['title'][0]['plain_text']
                elif v['type'] == 'rich_text' and len(v['rich_text']) > 0:
                    text_parts = [r['plain_text'] for r in v['rich_text']]
                    desc += " ".join(text_parts) + " "
                elif v['type'] == 'multi_select':
                    desc += ", ".join([opt['name'] for opt in v['multi_select']]) + " "
            
            print(f"Position: {title_text}")
            if desc:
                print(f"Details: {desc}")
    except Exception as e:
        print(f"Error reading {name}: {e}")
    print()
