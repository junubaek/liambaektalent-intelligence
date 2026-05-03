import json
import requests
import sys

# Set encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Load secrets
with open('secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)

headers = {
    'Authorization': f'Bearer {s["NOTION_API_KEY"]}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

# PROJECT DB에서 포지션 이름 가져오기
url = 'https://api.notion.com/v1/databases/1ef4807f4b584fecab665c2e593b1ca4/query'
all_pages = []
payload = {'page_size': 100}

print("Fetching position names from PROJECT DB...")
while True:
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        print(f"Error: {r.text}")
        break
    data = r.json()
    all_pages.extend(data.get('results', []))
    if not data.get('has_more'):
        break
    payload['start_cursor'] = data.get('next_cursor')

print(f'총 포지션: {len(all_pages)}개 로드 완료.\n')

for page in all_pages:
    pid = page['id']
    props = page.get('properties', {})
    
    # 이름
    name_list = props.get('이름', {}).get('title', [])
    name = name_list[0].get('plain_text', '') if name_list else 'No Name'
    
    # 상태
    status = props.get('상태', {}).get('status', {}).get('name', 'N/A')
    
    print(f'{pid[:8]} | {name} | {status}')
