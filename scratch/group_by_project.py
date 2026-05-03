import json
import requests
import sys
from collections import defaultdict

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

# PROGRAM DB 전체 가져오기
url = 'https://api.notion.com/v1/databases/756285ea-c39e-4315-8530-8e4154488d03/query'
all_pages = []
payload = {'page_size': 100}

print("Fetching data from PROGRAM DB...")
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

print(f'총 {len(all_pages)}건 로드 완료.\n')

# 포지션(PROJECT)별 그룹핑
positions = defaultdict(list)

for page in all_pages:
    props = page.get('properties', {})
    
    # 후보자명
    name_list = props.get('후보자', {}).get('title', [])
    name = name_list[0].get('plain_text', '') if name_list else ''
    
    # 전형단계
    stage = props.get('전형', {}).get('status', {}).get('name', '')
    
    # 프로젝트 (포지션)
    proj_list = props.get('PROJECT', {}).get('relation', [])
    proj_id = proj_list[0].get('id', 'unknown') if proj_list else 'unknown'
    
    if name and stage:
        positions[proj_id].append({'name': name, 'stage': stage})

# 출력
for pid, candidates in positions.items():
    print(f'Project {pid}:')
    for c in candidates:
        print(f'  - {c["name"]} | {c["stage"]}')
    print()
