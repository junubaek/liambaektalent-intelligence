import json, sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))
all_ids = set()
for item in d:
    for rid in (item.get('relevant_ids') or []):
        all_ids.add(rid)

cur.execute('''
    SELECT id, name_kr, total_years, sector,
           profile_summary, google_drive_url
    FROM candidates
    WHERE id IN ({})
    AND (profile_summary IS NULL OR profile_summary = ''
         OR sector IS NULL OR sector = '')
    AND is_duplicate = 0
'''.format(','.join('?'*len(all_ids))), list(all_ids))

rows = cur.fetchall()
print(f'재파싱 대상: {len(rows)}명')
for r in rows:
    print(f'  {r["name_kr"]} | {r["total_years"]}년 | sector={r["sector"]} | drive={bool(r["google_drive_url"])}')
conn.close()
