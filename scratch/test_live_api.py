import requests
import json

BASE = 'https://liambaektalent-intelligence-production.up.railway.app'

print("Logging in to live Railway API...")
# 로그인
r = requests.post(f'{BASE}/api/auth/login', 
    json={'id':'liam','password':'liam1234'}, timeout=15)
print('login status:', r.status_code)
token = r.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("\nSearching for 'System Software Architect'...")
# System Software Architect 검색
r = requests.post(f'{BASE}/api/search-v8',
    json={'prompt':'System Software Architect','sectors':[],'seniority':['All'],'required':[],'preferred':[]},
    headers=H, timeout=30)
results = r.json().get('matched', [])
print(f'Total search results returned: {len(results)}')

# 김국현, 이원철, 한상현 찾기
found_any = False
for i, c in enumerate(results):
    name = c.get('name_kr') or c.get('name','')
    if '김국현' in name or '이원철' in name or '한상현' in name:
        found_any = True
        print(f"\n[Rank {i+1}] {name}")
        print(f"  sector: {c.get('sector')}")
        print(f"  company: {c.get('current_company')}")
        print(f"  summary: {str(c.get('profile_summary',''))[:120]}")

if not found_any:
    print("\nNone of the target candidates (김국현, 이원철, 한상현) were found in the search results.")
