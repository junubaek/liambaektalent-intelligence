import sqlite3
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute("""
    SELECT id, name_kr, email, current_company, created_at, is_duplicate,
           careers_json, profile_summary, total_years
    FROM candidates
    WHERE name_kr IS NOT NULL AND name_kr != ''
    ORDER BY name_kr, created_at
""")
rows = cur.fetchall()

# 이름별 그룹핑
groups = defaultdict(list)
for row in rows:
    name = row[1].strip() if row[1] else ''
    if not name:
        continue

    # career_json 경력 개수 계산
    career_count = 0
    try:
        careers = json.loads(row[6]) if row[6] else []
        career_count = len(careers) if isinstance(careers, list) else 0
    except:
        career_count = 0

    groups[name].append({
        'id': row[0],
        'name_kr': row[1],
        'email': row[2],
        'current_company': row[3],
        'created_at': row[4],
        'is_duplicate': row[5],
        'career_count': career_count,
        'has_summary': 1 if row[7] and len(row[7].strip()) > 10 else 0,
        'total_years': row[8] or 0,
    })

duplicates = {name: records for name, records in groups.items() if len(records) > 1}

def score_record(r):
    """마스터 적합도 점수 계산"""
    score = 0
    score += r['career_count'] * 10      # 경력 개수 (가장 중요)
    score += r['has_summary'] * 5         # 요약 있음
    score += min(r['total_years'], 30)    # 경력 연수 (최대 30점)
    return score

# 분석 결과 저장
wrong_master = []   # 현재 마스터가 최선이 아닌 케이스
ok_master = []      # 현재 마스터가 이미 최선인 케이스

for name, records in duplicates.items():
    # 점수 기준으로 최선 레코드 찾기
    best = max(records, key=lambda r: (score_record(r), r['created_at'] or ''))
    current_masters = [r for r in records if r['is_duplicate'] == 0]

    if not current_masters:
        # 마스터가 없는 케이스 → best를 마스터로
        wrong_master.append({'name': name, 'records': records, 'best_id': best['id']})
    elif len(current_masters) > 1:
        # 마스터가 여러 개 → best 하나만 남기기
        wrong_master.append({'name': name, 'records': records, 'best_id': best['id']})
    else:
        current_master = current_masters[0]
        if current_master['id'] != best['id']:
            # 현재 마스터가 최선이 아님 → 교체 필요
            wrong_master.append({'name': name, 'records': records, 'best_id': best['id']})
        else:
            ok_master.append(name)

print(f"=== 중복 마스터 재판정 결과 ===")
print(f"전체 중복 이름: {len(duplicates)}명")
print(f"현재 마스터가 최선: {len(ok_master)}명")
print(f"마스터 교체 필요: {len(wrong_master)}명")
print()

# 교체 필요 케이스 상세 출력 (상위 20개)
print("=== 교체 필요 케이스 (상위 20개 미리보기) ===")
for item in wrong_master[:20]:
    print(f"[{item['name']}]")
    for r in item['records']:
        is_best = '★ 새 마스터' if r['id'] == item['best_id'] else ''
        is_cur = '[현재마스터]' if r['is_duplicate'] == 0 else '[구버전]'
        print(f"  {is_cur} ID: {r['id'][:8]}... | current: {r['current_company']} | "
              f"경력:{r['career_count']}개 | 연수:{r['total_years']}년 | "
              f"요약:{r['has_summary']} | created: {r['created_at']} {is_best}")
    print()

# ─────────────────────────────────────────
# 실제 DB 업데이트 (확인 후 진행)
# ─────────────────────────────────────────
print("=" * 50)
response = input(f"위 내용으로 DB 업데이트 진행할까요? (yes 입력 시 실행): ").strip().lower()

if response != 'yes':
    print("취소됨. DB 변경 없음.")
    conn.close()
    sys.exit()

updated = 0
for item in wrong_master:
    best_id = item['best_id']
    for r in item['records']:
        if r['id'] == best_id:
            cur.execute("UPDATE candidates SET is_duplicate = 0 WHERE id = ?", (r['id'],))
        else:
            cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE id = ?", (r['id'],))
        updated += 1

conn.commit()
print(f"\\n완료. {updated}개 레코드 업데이트됨.")
print(f"마스터(is_duplicate=0): {len(wrong_master) + len(ok_master)}명")
print(f"구버전(is_duplicate=1): {sum(len(v['records']) for v in wrong_master) + sum(len(groups[n]) - 1 for n in ok_master)}개")

conn.close()
