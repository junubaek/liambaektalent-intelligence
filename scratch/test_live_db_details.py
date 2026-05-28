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

# 1. Test /api/quick-search
print("\n--- Testing /api/quick-search?q=김국현 ---")
try:
    r_qs = requests.get(f'{BASE}/api/quick-search?q=김국현', headers=H, timeout=15)
    print("Status:", r_qs.status_code)
    print("Response JSON:")
    print(json.dumps(r_qs.json(), ensure_ascii=False, indent=2))
except Exception as e:
    print("Error /api/quick-search:", e)

# 2. Test /api/candidates
print("\n--- Testing /api/candidates?query=김국현 ---")
try:
    r_c = requests.get(f'{BASE}/api/candidates?query=김국현', headers=H, timeout=15)
    print("Status:", r_c.status_code)
    print("Response JSON:")
    # Print first few elements or truncated output safely
    print(json.dumps(r_c.json()[:3] if isinstance(r_c.json(), list) else r_c.json(), ensure_ascii=False, indent=2))
except Exception as e:
    print("Error /api/candidates:", e)
