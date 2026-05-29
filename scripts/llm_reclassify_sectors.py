import sqlite3, sys, json, os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

# secrets.json에서 OPENAI_API_KEY 로드
secrets_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json'
try:
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        if 'OPENAI_API_KEY' in secrets:
            os.environ['OPENAI_API_KEY'] = secrets['OPENAI_API_KEY']
except Exception as e:
    print(f"secrets.json 로드 에러: {e}")

STANDARD_SECTORS = [
    'Eng_SW', 'Eng_AI', 'Eng_Data', 'Eng_Embedded',
    'Eng_HW', 'Eng_Semi', 'Product', 'Finance',
    'Marketing', 'Sales', 'HR', 'Strategy',
    'Operations', 'Legal', 'Healthcare'
]

client = OpenAI()
db_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 미매핑 후보자 가져오기
cur.execute("""
    SELECT id, sector, profile_summary, name_kr
    FROM candidates
    WHERE sector NOT IN (
        'Eng_SW','Eng_AI','Eng_Data','Eng_Embedded',
        'Eng_HW','Eng_Semi','Product','Finance',
        'Marketing','Sales','HR','Strategy',
        'Operations','Legal','Healthcare'
    )
    AND sector IS NOT NULL
""")
rows = cur.fetchall()
print(f'LLM 분류 대상: {len(rows)}명')
conn.close()

def classify_one(id_, old_sector, summary, name):
    prompt = f"""
다음 후보자의 직무 sector를 아래 표준 목록 중에서 골라줘.
복수 가능 (최대 2개), 주전공 먼저. 쉼표로 구분.
반드시 아래 목록에서만 선택해.

표준 sector:
Eng_SW: 백엔드/프론트엔드/DevOps/인프라/플랫폼 엔지니어
Eng_AI: ML/DL/LLM/MLOps/AI연구
Eng_Data: 데이터엔지니어/사이언티스트/분석가
Eng_Embedded: 펌웨어/BSP/RTOS/임베디드
Eng_HW: 회로설계/PCB/RF/제조엔지니어링
Eng_Semi: RTL/SoC/NPU/ASIC 반도체 설계
Product: PM/PO/서비스기획
Finance: 재무/FP&A/회계/IR/자금
Marketing: 브랜드/그로스/퍼포먼스/CRM
Sales: B2B영업/엔터프라이즈세일즈
HR: 채용/HRBP/조직문화/총무
Strategy: 경영전략/BD/사업개발/컨설팅
Operations: SCM/물류/구매/제조생산관리
Legal: 법무/컴플라이언스
Healthcare: 제약/바이오/의료기기

현재 sector: {old_sector}
요약: {summary or '없음'}

JSON으로만 답해: {{"sector": "Primary" 또는 "Primary, Secondary"}}
"""
    try:
        res = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=30,
            temperature=0
        )
        raw = res.choices[0].message.content.strip()
        parsed = json.loads(raw.replace('```json','').replace('```','').strip())
        new_sector = parsed.get('sector', old_sector)
        return (new_sector, id_, name, old_sector, True)
    except Exception as e:
        return (old_sector, id_, name, old_sector, False)

# ThreadPoolExecutor를 이용해 병렬 처리 (30개 스레드)
updates = []
success_count = 0
failed_count = 0

print("병렬 분류 작업을 시작합니다...")
with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(classify_one, id_, old_sector, summary, name) for id_, old_sector, summary, name in rows]
    for idx, future in enumerate(as_completed(futures), 1):
        new_sector, id_, name, old_sector, success = future.result()
        updates.append((new_sector, id_))
        if success:
            success_count += 1
            print(f"[{idx}/{len(rows)}] {name}: {old_sector} → {new_sector}")
        else:
            failed_count += 1
            print(f"[{idx}/{len(rows)}] {name} 실패")

# DB 일괄 업데이트
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.executemany("UPDATE candidates SET sector = ? WHERE id = ?", updates)
conn.commit()

print(f'\n완료: 총 {len(updates)}명 처리 (성공: {success_count}명, 실패: {failed_count}명) 업데이트 완료.')
conn.close()
