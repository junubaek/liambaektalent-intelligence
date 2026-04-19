import json
import urllib.request
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

url = f"https://api.notion.com/v1/databases/{secrets['NOTION_DATABASE_ID']}"
headers = {
    'Authorization': f"Bearer {secrets['NOTION_API_KEY']}",
    'Notion-Version': '2022-06-28'
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as res:
    schema = json.loads(res.read().decode('utf-8'))
    props = schema.get('properties', {})
    
    print('=== 메인 섹터 (Main Sectors) ===')
    if 'Main Sectors' in props:
        opts = props['Main Sectors'].get('multi_select', {}).get('options', [])
        for opt in opts:
            print(f"- {opt['name']}")
            
    print('\n=== 서브 섹터 (Sub Sectors) ===')
    if 'Sub Sectors' in props:
        opts = props['Sub Sectors'].get('multi_select', {}).get('options', [])
        for opt in opts:
            print(f"- {opt['name']}")
