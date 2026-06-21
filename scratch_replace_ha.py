import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = 'golden_dataset_v9.json'
d = json.load(open(path, encoding='utf-8'))

for item in d:
    if item.get('query') == 'on-device AI inference embedded AI semiconductor':
        item['query'] = 'Custom IP SoC chip architecture mass production silicon'
        print(f'교체 완료: {item["query"]}')
        print(f'정답: {item["relevant_ids"]}')

json.dump(d, open(path,'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("golden_dataset_v9.json 쿼리 교체 및 저장 완료.")
