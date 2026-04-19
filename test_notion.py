import urllib.request
import json

d = json.load(open('secrets.json', 'r', encoding='utf-8'))
db_id = d['NOTION_DATABASE_ID']
token = d['NOTION_API_KEY']
req = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{db_id}/query", 
    data=json.dumps({"page_size": 1}).encode('utf-8'), 
    headers={
        'Authorization': 'Bearer '+token, 
        'Notion-Version': '2022-06-28', 
        'Content-Type': 'application/json'
    }, 
    method='POST'
)
res = urllib.request.urlopen(req)
data = json.loads(res.read())
keys = list(data['results'][0]['properties'].keys())
with open('keys.txt', 'w', encoding='utf-8') as f:
    f.write(json.dumps(keys, ensure_ascii=False))
