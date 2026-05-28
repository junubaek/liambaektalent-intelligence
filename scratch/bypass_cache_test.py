import requests
import json

BASE = 'https://liambaektalent-intelligence-production.up.railway.app'

print("Logging in to live Railway API...")
r = requests.post(f'{BASE}/api/auth/login', 
    json={'id':'liam','password':'liam1234'}, timeout=15)
token = r.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Using a modified query to bypass memory cache
prompt = 'System Software Architect BSP SoC Qualcomm'
print(f"\nSearching with un-cached query: '{prompt}'...")

r = requests.post(f'{BASE}/api/search-v8',
    json={'prompt': prompt,'sectors':[],'seniority':['All'],'required':[],'preferred':[]},
    headers=H, timeout=30)

results = r.json().get('matched', [])
print(f'Total matches: {len(results)}')

for i, c in enumerate(results[:5]):
    print(f"\n[Rank {i+1}] {c.get('name_kr') or c.get('name')} | id: {c.get('id', '')}")
    print(f"  sector: {c.get('sector')}")
    print(f"  company: {c.get('current_company')}")
    print(f"  summary: {str(c.get('profile_summary', ''))[:120]}")
