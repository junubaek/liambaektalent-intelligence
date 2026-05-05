import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['배근호', '성장현', '남규한', '이정우', '이예지', '김광우', '김완희']

print("=== 1. Neo4j 동기화 상태 확인 ===\n")
for name in targets:
    cur.execute("""
        SELECT id, name_kr, current_company, profile_summary,
               is_neo4j_synced, is_pinecone_synced, is_duplicate
        FROM candidates
        WHERE name_kr LIKE ?
        ORDER BY is_duplicate ASC
    """, (f'%{name}%',))
    rows = cur.fetchall()
    for r in rows:
        cid, nm, company, summary, neo4j, pinecone, is_dup = r
        master = "✅ 마스터" if is_dup == 0 else "❌ 구버전"
        print(f"[{nm}] {master}")
        print(f"  current_company  : {company}")
        print(f"  profile_summary  : {'있음' if summary and len(summary) > 10 else '❌ 없음'}")
        print(f"  is_neo4j_synced  : {neo4j}")
        print(f"  is_pinecone_synced: {pinecone}")
        print()

print("\n=== 2. 남규한 마스터 승격 ===\n")
# 남규한 중복 레코드 중 가장 데이터 풍부한 것을 마스터로
cur.execute("""
    SELECT id, name_kr, current_company, careers_json, profile_summary
    FROM candidates WHERE name_kr LIKE '%남규한%'
""")
rows = cur.fetchall()

best = None
best_score = -1
for r in rows:
    cid, nm, company, career_json, summary = r
    score = 0
    try:
        careers = json.loads(career_json) if career_json else []
        score += len(careers) * 10
    except:
        pass
    if summary and len(summary) > 10:
        score += 5
    if company:
        score += 3
    if score > best_score:
        best_score = score
        best = r

if best:
    print(f"승격 대상: {best[0][:8]}... | {best[2]} | 점수: {best_score}")
    cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE name_kr LIKE '%남규한%'")
    cur.execute("UPDATE candidates SET is_duplicate = 0, is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE id = ?", (best[0],))
    conn.commit()
    print("✅ 남규한 마스터 승격 완료 → 재색인 대상으로 마킹")
else:
    print("❌ 남규한 레코드 없음")

print("\n=== 3. 이예지 profile_summary 재생성 대상 마킹 ===\n")
cur.execute("""
    SELECT id, name_kr, raw_text FROM candidates
    WHERE name_kr LIKE '%이예지%' AND is_duplicate = 0
""")
row = cur.fetchone()
if row:
    cid, nm, raw_text = row
    if raw_text and len(raw_text) > 100:
        # raw_text 앞 200자로 임시 summary 생성
        temp_summary = raw_text.strip()[:200].replace('\n', ' ')
        cur.execute("UPDATE candidates SET profile_summary = ?, is_pinecone_synced = 0 WHERE id = ?",
                    (temp_summary, cid))
        conn.commit()
        print(f"✅ 이예지 임시 summary 주입 완료: {temp_summary[:80]}...")
    else:
        print("❌ 이예지 raw_text 없음, 수동 확인 필요")
else:
    print("❌ 이예지 마스터 레코드 없음")

print("\n=== 4. 김광우/김완희 current_company raw_text 확인 ===\n")
for name in ['김광우', '김완희']:
    cur.execute("""
        SELECT id, name_kr, current_company, raw_text
        FROM candidates WHERE name_kr LIKE ? AND is_duplicate = 0
    """, (f'%{name}%',))
    row = cur.fetchone()
    if row:
        cid, nm, company, raw_text = row
        print(f"[{nm}]")
        print(f"  current_company: {company}")
        print(f"  raw_text 앞 300자:")
        print(f"  {raw_text[:300].replace(chr(10), ' ') if raw_text else '없음'}")
        print()

conn.close()
print("완료.")
