import time, requests

url = 'https://liambaektalent-intelligence-production.up.railway.app/api/search-v8'

# 로그인
r = requests.post(
    'https://liambaektalent-intelligence-production.up.railway.app/api/auth/login',
    json={'id':'liam','password':'liam1234'})

if 'token' not in r.json():
    print("로그인 실패:", r.text)
    exit()
    
token = r.json()['token']
H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

payload = {'prompt':'재무 CFO 자금 운용','sectors':[],
           'seniority':['All'],'required':[],'preferred':[]}

print("=== 첫 번째 검색 시작 (캐시 미스 예상) ===")
t1 = time.time()
try:
    requests.post(url, json=payload, headers=H, timeout=60)
except Exception as e:
    print(f"1차 검색 에러: {e}")
t2 = time.time()
print(f'첫 번째 검색: {t2-t1:.2f}초')

print("=== 두 번째 검색 시작 (캐시 히트 예상) ===")
t3 = time.time()
try:
    requests.post(url, json=payload, headers=H, timeout=30)
except Exception as e:
    print(f"2차 검색 에러: {e}")
t4 = time.time()
print(f'두 번째 검색: {t4-t3:.2f}초')

if (t4-t3) > 0:
    print(f'속도 향상: {(t2-t1)/(t4-t3):.1f}배')
