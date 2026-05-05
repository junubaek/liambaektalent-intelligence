import json, sqlite3, sys, time, os
from openai import OpenAI

# Set output encoding to utf-8 for Windows compatibility
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load OpenAI API Key from secrets.json
secrets_path = 'secrets.json'
if not os.path.exists(secrets_path):
    print("Error: secrets.json not found.")
    sys.exit(1)

try:
    s = json.load(open(secrets_path, 'r', encoding='utf-8'))
    client = OpenAI(api_key=s['OPENAI_API_KEY'])
except Exception as e:
    print(f"Error loading secrets or initializing OpenAI client: {e}")
    sys.exit(1)

# 회사명 정규화 함수
def normalize_company(name):
    import re
    if not name: return ""
    name = name.strip()
    # 법인격 접미사/접두사 제거
    name = re.sub(r'\(주\)|㈜|\(유\)|주식회사|Co\.,?\s*Ltd\.?|Inc\.?|\(주\)$', '', name)
    name = re.sub(r'^(주식회사|㈜)\s*', '', name)
    name = name.strip()
    # 영문 → 한글 매핑 (일반적인 케이스)
    mapping = {
        'Samsung Electronics': '삼성전자',
        'Coupang': '쿠팡',
        'Kakao': '카카오',
        'LG Electronics': 'LG전자',
        'SK Hynix': 'SK하이닉스',
    }
    return mapping.get(name, name)

# LLM으로 회사 분석
def analyze_company(company_name):
    prompt = f"""회사명: {company_name}

아래 JSON 형식으로만 답해줘. 다른 말 하지 마.

{{
  "scale": "스타트업|중견기업|대기업|글로벌대기업",
  "revenue_tier": "<100억|100억~1000억|1000억~1조|1조+|알수없음",
  "employee_tier": "<50명|50~500명|500~5000명|5000명+|알수없음",
  "sector": "IT|금융|제조|컨설팅|커머스|게임|바이오|기타",
  "inferred_skills": {{
    "backend": ["대용량_트래픽이 예상되면 추가", "MSA"],
    "finance": ["운용자금_규모가 크면 추가"],
    "general": ["글로벌경험 있으면 추가"]
  }},
  "major_events": {{
    "2020": "예: IPO 또는 대형 M&A 있으면 기재",
    "2021": ""
  }},
  "traffic_scale": "소규모|중규모|대규모|초대규모|해당없음",
  "notable": "회사 특이사항 한줄"
}}"""
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0
    )
    
    text = response.choices[0].message.content.strip()
    # JSON 파싱 (코드 블록 제거 로직)
    if '```' in text:
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:].strip()
        else:
            text = text.strip()
    
    return json.loads(text)

# 상위 100개 회사 분석
db_path = 'candidates.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('''
    SELECT current_company, COUNT(*) as cnt
    FROM candidates
    WHERE current_company IS NOT NULL
    AND current_company NOT IN ('미상', '', '프리랜서')
    GROUP BY current_company
    ORDER BY cnt DESC
    LIMIT 100
''')
companies = cur.fetchall()

# company_intelligence 테이블 생성
cur.execute('''
    CREATE TABLE IF NOT EXISTS company_intelligence (
        company_name TEXT PRIMARY KEY,
        normalized_name TEXT,
        scale TEXT,
        revenue_tier TEXT,
        employee_tier TEXT,
        sector TEXT,
        inferred_skills TEXT,
        major_events TEXT,
        traffic_scale TEXT,
        notable TEXT,
        analyzed_at TEXT
    )
''')
conn.commit()

print(f'총 {len(companies)}개 회사 분석 시작...')
success = 0
for company, cnt in companies:
    normalized = normalize_company(company)
    
    # 이미 분석된 회사 스킵
    cur.execute('SELECT 1 FROM company_intelligence WHERE company_name=?', (company,))
    if cur.fetchone():
        # print(f'스킵 (이미 분석됨): {company}')
        continue
    
    try:
        result = analyze_company(normalized)
        cur.execute('''
            INSERT OR REPLACE INTO company_intelligence
            (company_name, normalized_name, scale, revenue_tier, employee_tier,
             sector, inferred_skills, major_events, traffic_scale, notable, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (
            company, normalized,
            result.get('scale',''),
            result.get('revenue_tier',''),
            result.get('employee_tier',''),
            result.get('sector',''),
            json.dumps(result.get('inferred_skills',{}), ensure_ascii=False),
            json.dumps(result.get('major_events',{}), ensure_ascii=False),
            result.get('traffic_scale',''),
            result.get('notable',''),
        ))
        conn.commit()
        print(f'완료: {normalized} ({company}) | {result.get("scale")} | {result.get("traffic_scale")} | {result.get("notable","")}')
        success += 1
        time.sleep(0.3)
    except Exception as e:
        print(f'에러: {normalized} | {e}')

conn.close()
print(f'\n완료: {success}개 회사 분석됨')
