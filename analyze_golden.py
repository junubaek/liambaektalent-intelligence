import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load the golden dataset
try:
    with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# 1. Total cases
total_cases = len(golden_data)
print(f"1. 총 케이스 (항목) 수: {total_cases}")

# Group by queries for analysis
q_map = {}
for idx, entry in enumerate(golden_data):
    if not isinstance(entry, dict):
        continue
    q = entry.get('jd_query', '')
    name = entry.get('candidate_name', 'Unknown')
    label = entry.get('label', '')
    
    if q not in q_map:
        q_map[q] = {'positive': [], 'negative': []}
        
    if label == 'positive':
        q_map[q]['positive'].append(name)
    elif label == 'negative':
        q_map[q]['negative'].append(name)

# 2. Positive/Negative per query
print("\n2. 쿼리별 Positive / Negative 후보자 수 (상위 15개 쿼리만 출력)")
queries = list(q_map.keys())
for q in queries[:15]:
    pos = q_map[q]['positive']
    neg = q_map[q]['negative']
    print(f"  - [{q}] : Positive {len(pos)}명 / Negative {len(neg)}명")

# 3. "Kubernetes OpenStack Terraform"
target_q = "Kubernetes OpenStack Terraform"
if target_q in q_map:
    print(f"\n3. '{target_q}' 쿼리의 Positive 정답자 전체:")
    print(f"   -> {q_map[target_q]['positive']}")
else:
    print(f"\n3. '{target_q}' 쿼리가 존재하지 않습니다.")

# 4. Check '최호진' and see what position he was registered for
print("\n4. 최호진 후보자의 연결 정보 (어느 포지션으로 등록됐는지):")
found_hojin = False
for entry in golden_data:
    if entry.get('candidate_name') == '최호진':
        found_hojin = True
        print(f"   - 쿼리(포지션): {entry.get('jd_query')}")
        print(f"   - 단계(Stage): {entry.get('stage')}")
        print(f"   - 회사/파일명: {entry.get('company')} / {entry.get('raw_filename')}")

if not found_hojin:
    print("   -> 최호진 후보자를 찾을 수 없습니다.")

