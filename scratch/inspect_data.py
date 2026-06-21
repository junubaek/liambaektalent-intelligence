import json, glob, sqlite3

print("=== [1] 기존 골든 데이터셋 전체 현황 파악 ===")
for path in sorted(glob.glob('golden_dataset_v*.json')):
    try:
        data = json.load(open(path, encoding='utf-8'))
        print(f'\n{path}')
        print(f'  쿼리 수: {len(data)}')
        for q in data:
            query = q.get('query', '') or q.get('jd_query', '')
            # Try to get targets name
            targets = q.get('relevant_names', []) or \
                      [c.get('name_kr','') for c in q.get('relevant_candidates',[])]
            print(f'  - {query} → {targets[:3]}')
    except Exception as e:
        print(f"Error reading {path}: {e}")

print("\n=== [2] CEI Tier A < S 분포 이상 분석 ===")
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Tier S로 분류된 회사들 샘플
cur.execute("""
    SELECT name_kr,
           json_extract(cei_json, '$.company_signal.tier') as tier,
           json_extract(cei_json, '$.company_signal.summary') as summary,
           current_company
    FROM candidates
    WHERE is_duplicate=0
    AND json_extract(cei_json, '$.company_signal.tier') = 'S'
    ORDER BY RANDOM()
    LIMIT 20
""")
print('=== Tier S 샘플 ===')
for r in cur.fetchall():
    print(f'  {r[0]} | {r[3]} → {r[2]}')

# Tier A 샘플
cur.execute("""
    SELECT name_kr,
           json_extract(cei_json, '$.company_signal.summary') as summary,
           current_company
    FROM candidates
    WHERE is_duplicate=0
    AND json_extract(cei_json, '$.company_signal.tier') = 'A'
    ORDER BY RANDOM()
    LIMIT 20
""")
print('\n=== Tier A 샘플 ===')
for r in cur.fetchall():
    print(f'  {r[0]} | {r[2]} → {r[1]}')

conn.close()
