import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = 'golden_dataset_v9.json'
d = json.load(open(path, encoding='utf-8'))

rollback_map = {
    'NoC Network_on_Chip interconnect SoC fabric performance simulation':
        'SoC NoC Network_on_Chip Chiplet semiconductor architect',
    'IPO_Preparation IR equity fundraising listing finance':
        'IPO preparation investor relations finance CFO fundraising',
    'CISO_CPO_Leadership information security game platform':
        'CISO information security game company',
    'GPU_Direct KubeVirt vDPA AI datacenter private cloud':
        'GPU virtualization AI datacenter HPC network infra',
}

for item in d:
    q = item.get('query','')
    if q in rollback_map:
        item['query'] = rollback_map[q]
        print(f'롤백: {item["query"]}')

json.dump(d, open(path,'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('롤백 완료')
