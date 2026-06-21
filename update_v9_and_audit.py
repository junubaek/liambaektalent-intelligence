import json
import sqlite3
import sys

def update_v9():
    path = 'golden_dataset_v9.json'
    d = json.load(open(path, encoding='utf-8'))

    remove_ids = {
        'bb55fc1a-c237-433e-9ef6-e79584cbb347',  # 백명석
    }

    add_ids = [
        '0c07f1bc-8d5c-4c36-82fa-14de5ca79ba0',  # 한원식
        'cf6f1c20-0b8b-4995-9abb-4b8cb81c3628',  # 이호석
        '2bc346d4-2f24-4f12-b90a-ca75441a3e49',  # 강형구
    ]

    for item in d:
        if 'CTO' in item.get('query',''):
            old = item.get('relevant_ids', [])
            cleaned = [x for x in old if x not in remove_ids]
            merged = list(dict.fromkeys(cleaned + add_ids))
            item['relevant_ids'] = merged
            print(f'쿼리: {item["query"]}')
            print(f'  이전: {old}')
            print(f'  이후: {merged}')

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print('golden_dataset_v9.json 저장 완료\n')

def audit_missing_drive_links():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT count(*)
        FROM candidates
        WHERE is_duplicate=0
        AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')
    """)
    total_missing = cur.fetchone()[0]
    print(f"=== 구글 드라이브 링크 미연결 활성 후보자 수: {total_missing}명 ===\n")

    cur.execute("""
        SELECT id, name_kr, current_company, sector, total_years
        FROM candidates
        WHERE is_duplicate=0
        AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')
        ORDER BY name_kr
    """)
    rows = cur.fetchall()
    
    # We will print the list. Limit output to prevent context bloating, but show enough.
    # Let's print the first 100 as a representative list and sum the rest.
    print(f"상세 명단 (가나다순, 최대 100명 출력):")
    for i, r in enumerate(rows[:100]):
        print(f"  {i+1}. {r[1]} | 회사: {r[2] or '없음'} | sector: {r[3] or '없음'} | 연차: {r[4]}년 | ID: {r[0]}")
    
    if len(rows) > 100:
        print(f"  ... 외 {len(rows) - 100}명 생략")

    conn.close()

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    update_v9()
    audit_missing_drive_links()
