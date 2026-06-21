import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = 'golden_dataset_v9.json'
d = json.load(open(path, encoding='utf-8'))

# 쿼리 교체 매핑
replace_map = {
    'SCM logistics operations cost management':
        'contract negotiation cost structure financial planning operations',
    'IPO IR strategic planning fundraising finance':
        'IPO preparation investor relations finance CFO fundraising',
}

for item in d:
    q = item.get('query', '')
    if q in replace_map:
        new_q = replace_map[q]
        print(f'교체: {q}')
        print(f'  → {new_q}')
        item['query'] = new_q

json.dump(d, open(path,'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('저장 완료')

# Find files related to ndcg evaluation
eval_files = [f for f in os.listdir('.') if 'ndcg' in f or 'eval' in f]
print("관련 평가 파일 목록:", eval_files)
