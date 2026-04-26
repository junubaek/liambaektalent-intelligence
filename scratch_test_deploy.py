import requests, time

BASE = 'https://liambaektalent-intelligence-production.up.railway.app'

print('배포 대기 중... (90초)')
time.sleep(90)

# 로그인
r = requests.post(f'{BASE}/api/auth/login',
    json={'id':'liam','password':'liam1234'}, timeout=15)
token = r.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 검색 테스트
tests = [
    ('CFO 재무총괄 IPO 자금조달', 'SENIOR'),
    ('DevOps Kubernetes 인프라', 'All'),
    ('세무 법인세 부가세', 'JUNIOR'),
    ('채용 TA 소싱 온보딩', 'All'),
]

print()
for prompt, seniority in tests:
    r = requests.post(f'{BASE}/api/search-v8',
        json={'prompt':prompt,'sectors':[],'seniority':[seniority],
              'required':[],'preferred':[]},
        headers=H, timeout=30)
    d = r.json()
    matched = d.get('matched', [])
    top = matched[0] if matched else {}
    name = top.get('이름') or top.get('name_kr','?')
    score = top.get('score',0)
    print(f'[{seniority}] {prompt[:30]}')
    print(f'  → 1위: {name} | score={score:.1f} | 결과:{len(matched)}명')
