import sqlite3, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

print("=== 1. 전체 현황 ===")
cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0")
print("Active candidates:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=1")
print("Duplicates:", cur.fetchone()[0])

print("\n=== 2. 이름 인코딩 상태 ===")
cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (name_kr IS NULL OR name_kr='')")
print("name_kr 비어있음:", cur.fetchone()[0])
cur.execute("SELECT id, name_kr FROM candidates WHERE is_duplicate=0 LIMIT 10")
for r in cur.fetchall():
    print(r[0][:8], '|', r[1])

print("\n=== 3. 섹터 분포 ===")
cur.execute("SELECT sector, COUNT(*) as cnt FROM candidates WHERE is_duplicate=0 GROUP BY sector ORDER BY cnt DESC")
for r in cur.fetchall():
    print(r[0], '|', r[1])
print("\n=== 4. UI 핵심 컬럼 NULL 현황 ===")
for col in ['name_kr','current_title','current_company','raw_text','sector','total_years']:
    cur.execute(f"SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND ({col} IS NULL OR {col}='')")
    print(f"{col} 비어있음:", cur.fetchone()[0])

print("\n=== 5. 신규 이력서 인제스트 확인 (최근 등록 20개) ===")
cur.execute("SELECT id, name_kr, current_company, created_at FROM candidates WHERE is_duplicate=0 ORDER BY created_at DESC LIMIT 20")
for r in cur.fetchall():
    print(r[0][:8], '|', r[1], '|', r[2], '|', r[3])

conn.close()
