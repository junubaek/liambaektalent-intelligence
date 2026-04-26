import sqlite3, sys, os, json, time
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

genai.configure(api_key=secrets.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 전체 미파싱 대상
cur.execute('''
    SELECT id, name_kr, raw_text, google_drive_url
    FROM candidates
    WHERE is_duplicate=0
    AND (
        profile_summary IS NULL OR profile_summary = ''
        OR sector IS NULL OR sector = ''
        OR sector = '미분류'
    )
    ORDER BY ROWID
''')
targets = cur.fetchall()
print(f'전체 재파싱 대상: {len(targets)}명')
conn.close()

def parse_target(row):
    cid = row['id']
    name = row['name_kr'] or '이름없음'
    raw = (row['raw_text'] or '')[:3000]
    
    if len(raw) < 50:
        return cid, False, "", "", 0

    prompt = f'''아래 이력서에서 추출해줘. JSON만 반환.

이력서:
{raw}

추출 항목:
- profile_summary: 핵심역량 2문장 (한글, 개인정보 제외)
- sector: 주요 직군 (SW/Finance/HR/Marketing/Strategy/Operations/Legal/Semiconductor/Healthcare/Education 중 하나)
- total_years: 총 경력연수 (숫자만)

JSON 형식:
{{"profile_summary": "...", "sector": "...", "total_years": 0}}'''

    for attempt in range(3):
        try:
            resp = model.generate_content(prompt)
            text = resp.text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            parsed = json.loads(text.strip())
            summary = parsed.get('profile_summary', '')
            sector = parsed.get('sector', '')
            years = parsed.get('total_years', 0)
            return cid, True, summary, sector, years
        except Exception as e:
            time.sleep(2)
    return cid, False, "", "", 0

total_done = 0
total_fixed = 0

BATCH = 50
for i in range(0, len(targets), BATCH):
    batch = targets[i:i+BATCH]
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(parse_target, row): row for row in batch}
        for future in as_completed(futures):
            results.append(future.result())
            
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    for cid, ok, summary, sector, years in results:
        if ok and (summary or sector):
            cur.execute('''
                UPDATE candidates
                SET profile_summary=?,
                    sector=CASE WHEN sector IS NULL OR sector='' OR sector='미분류'
                           THEN ? ELSE sector END,
                    total_years=CASE WHEN total_years IS NULL OR total_years=0
                                THEN ? ELSE total_years END
                WHERE id=?
            ''', (summary, sector, years, cid))
            total_fixed += 1
    conn.commit()
    conn.close()
    
    total_done += len(batch)
    print(f'진행: {total_done}/{len(targets)}명 처리 | 수정: {total_fixed}명')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''
    SELECT COUNT(*) FROM candidates
    WHERE is_duplicate=0
    AND (profile_summary IS NULL OR profile_summary = ''
    OR sector IS NULL OR sector = '' OR sector = '미분류')
''')
remaining = cur.fetchone()[0]
print(f'\n완료! 남은 미파싱: {remaining}명')
print(f'총 수정: {total_fixed}명')
conn.close()
