import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['배근호', '성장현', '남규한', '이정우', '이예지', '김광우', '김완희']

for name in targets:
    cur.execute("""
        SELECT id, name_kr, current_company, profile_summary, sector,
               careers_json, raw_text, is_duplicate, is_parsed
        FROM candidates
        WHERE name_kr LIKE ? AND is_duplicate = 0
    """, (f'%{name}%',))
    rows = cur.fetchall()

    if not rows:
        print(f"[{name}] ❌ 마스터 레코드 없음 (is_duplicate=0 없음)")
        # 중복 포함해서 다시 찾기
        cur.execute("SELECT id, name_kr, current_company, is_duplicate, is_parsed FROM candidates WHERE name_kr LIKE ?", (f'%{name}%',))
        all_rows = cur.fetchall()
        for r in all_rows:
            print(f"  → ID: {r[0][:8]}... | current: {r[2]} | is_dup: {r[3]} | is_parsed: {r[4]}")
        print()
        continue

    for row in rows:
        cid, nm, company, summary, sector, career_json, raw_text, is_dup, is_parsed = row

        career_count = 0
        try:
            careers = json.loads(career_json) if career_json else []
            career_count = len(careers)
        except:
            pass

        has_raw = bool(raw_text and len(raw_text.strip()) > 50)
        has_summary = bool(summary and len(summary.strip()) > 10)

        print(f"[{nm}]")
        print(f"  ID: {cid[:8]}...")
        print(f"  current_company : {company}")
        print(f"  sector          : {sector}")
        print(f"  profile_summary : {'있음' if has_summary else '❌ 없음'}")
        print(f"  career_json     : {career_count}개")
        print(f"  raw_text        : {'있음' if has_raw else '❌ 없음'}")
        print(f"  is_parsed       : {is_parsed}")

        if career_json:
            try:
                careers = json.loads(career_json)
                for c in careers[:3]:
                    print(f"    - {c.get('company','?')} | {c.get('start_date','?')} ~ {c.get('end_date','?')}")
            except:
                pass
        print()

conn.close()
