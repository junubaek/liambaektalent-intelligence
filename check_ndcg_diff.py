import json

# 1. golden_dataset_v9.json count and queries
print("=== golden_dataset_v9.json ===")
try:
    with open('golden_dataset_v9.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f'golden_dataset_v9.json 총 쿼리 수: {len(d)}개')
    for item in d:
        print(f'  {item.get("query","")[:50]}')
except Exception as e:
    print("Error:", e)

# 2. scratch_eval_ndcg_v9.py top lines
print("\n=== scratch_eval_ndcg_v9.py top lines ===")
try:
    with open('scratch_eval_ndcg_v9.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines[:50]):
        print(f'{i+1}: {line}', end='')
except Exception as e:
    print("Error:", e)
