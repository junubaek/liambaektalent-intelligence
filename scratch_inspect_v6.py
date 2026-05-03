import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('golden_dataset_v6.json', encoding='utf-8'))
for item in d[:5]:
    q = item.get('query', item.get('jd_query', ''))
    ids = item.get('relevant_ids', [])
    print(q[:50])
    for i in ids:
        print('  ', i)
