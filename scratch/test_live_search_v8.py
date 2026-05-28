import requests
import json

BASE = 'https://liambaektalent-intelligence-production.up.railway.app'

print("Logging in to live Railway API...")
r = requests.post(f'{BASE}/api/auth/login', 
    json={'id':'liam','password':'liam1234'}, timeout=15)
print('login status:', r.status_code)
token = r.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("\nSearching via /api/search-v8 for 'System Software Architect BSP SoC'...")
r = requests.post(f'{BASE}/api/search-v8',
    json={'prompt':'System Software Architect BSP SoC','sectors':[],'seniority':['All'],'required':[],'preferred':[]},
    headers=H, timeout=30)

results = r.json().get('matched', [])
print(f'Total matches: {len(results)}')

for i, c in enumerate(results[:10]):
    name = c.get('name_kr') or c.get('name','')
    sector = c.get('sector','')
    company = c.get('current_company','')
    summary = c.get('profile_summary','')
    
    print(f"\n[Rank {i+1}] {name} | id: {c.get('id', '')[:8]}...")
    print(f"  sector: {sector}")
    print(f"  company: {company}")
    print(f"  summary: {str(summary)[:120]}")
