import json, sqlite3, sys, time
sys.stdout.reconfigure(encoding='utf-8')
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from incremental_ingest_v10 import MEGA_PROMPT, calculate_career_stats

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('''
    SELECT id, name_kr, raw_text, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND (
        profile_summary IS NULL OR profile_summary = ''
        OR sector IS NULL OR sector = ''
        OR sector = '미분류'
    )
    AND google_drive_url IS NOT NULL
    AND google_drive_url != ''
    LIMIT 200
''')
rows = cur.fetchall()
conn.close()

print(f'재파싱 대상: {len(rows)}명 (최대 200명 제한)')

def parse_candidate(r):
    cid = r["id"]
    name_kr = r["name_kr"]
    raw_text = r["raw_text"] or ""
    
    if len(raw_text) < 50:
        return cid, False, "too short", None, None, None, None
        
    parsed = None
    for attempt in range(3):
        try:
            prompt = MEGA_PROMPT.replace("{text}", f"[파일명: {name_kr}]\n\n" + raw_text[:6000])
            res = model.generate_content(prompt)
            raw = res.text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            break
        except Exception as e:
            time.sleep(2)
            
    if not parsed:
        return cid, False, "parsing failed", None, None, None, None
        
    sector = parsed.get("sector", "미분류")
    summary = parsed.get("summary", "")
    careers = parsed.get("careers_json", [])
    current_company, total_years = calculate_career_stats(careers)
    neo4j_edges = parsed.get("neo4j_edges", [])
    
    return cid, True, "", sector, summary, total_years, neo4j_edges

success = 0
failed = 0
total = 0

batch_size = 50
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    print(f"\n--- Batch {i//batch_size + 1} ({len(batch)}명) ---")
    
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(parse_candidate, r): r for r in batch}
        for future in as_completed(futures):
            r = futures[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                results.append((r["id"], False, str(e), None, None, None, None))
                
            total += 1
            if total % 10 == 0:
                print(f"진행상황: {total}/{len(rows)} 완료")
                
    # DB 업데이트
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    for cid, ok, msg, sector, summary, years, edges in results:
        if ok:
            cur.execute('''
                UPDATE candidates 
                SET sector=?, profile_summary=?, total_years=? 
                WHERE id=?
            ''', (sector, summary, years, cid))
            success += 1
        else:
            failed += 1
    conn.commit()
    conn.close()

print(f"\n완료. 성공: {success}, 실패: {failed}")

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''
    SELECT COUNT(*) FROM candidates
    WHERE is_duplicate=0
    AND (profile_summary IS NULL OR profile_summary = ''
    OR sector IS NULL OR sector = '' OR sector = '미분류')
''')
print('남은 미파싱:', cur.fetchone()[0], '명')
cur.execute('''
    SELECT COUNT(*) FROM candidates
    WHERE is_duplicate=0
    AND profile_summary IS NOT NULL
    AND profile_summary != ''
    AND sector IS NOT NULL
    AND sector != ''
    AND sector != '미분류'
''')
print('파싱 완료:', cur.fetchone()[0], '명')
conn.close()
