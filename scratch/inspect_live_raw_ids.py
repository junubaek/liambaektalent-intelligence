import requests
import json

BASE = 'https://liambaektalent-intelligence-production.up.railway.app'

print("Logging in to live Railway API...")
r = requests.post(f'{BASE}/api/auth/login', 
    json={'id':'liam','password':'liam1234'}, timeout=15)
token = r.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("\nSearching via /api/search-v8...")
r = requests.post(f'{BASE}/api/search-v8',
    json={'prompt':'System Software Architect BSP SoC','sectors':[],'seniority':['All'],'required':[],'preferred':[]},
    headers=H, timeout=30)

results = r.json().get('matched', [])
print(f"Total matches: {len(results)}")

# Print raw JSON for the top 5 candidates safely
for i, c in enumerate(results[:5]):
    print(f"\n--- Rank {i+1} ---")
    # We clean up binary or special characters if any, but UUIDs are safe ascii
    print("ID:", c.get('id'))
    print("Name:", repr(c.get('name_kr') or c.get('name')))
    print("Sector:", repr(c.get('sector')))
    print("Company:", repr(c.get('current_company')))
    print("Summary:", repr(c.get('profile_summary', '')[:80]))
