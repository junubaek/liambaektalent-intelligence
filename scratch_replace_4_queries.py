import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = 'golden_dataset_v9.json'
d = json.load(open(path, encoding='utf-8'))

replace_map = {
    'SoC NoC Network_on_Chip Chiplet semiconductor architect':
        'NoC Network_on_Chip interconnect SoC fabric performance simulation',
    'IPO preparation investor relations finance CFO fundraising':
        'IPO_Preparation IR equity fundraising listing finance',
    'CISO information security game company':
        'CISO_CPO_Leadership information security game platform',
    'GPU virtualization AI datacenter HPC network infra':
        'GPU_Direct KubeVirt vDPA AI datacenter private cloud',
}

for item in d:
    q = item.get('query','')
    if q in replace_map:
        new_q = replace_map[q]
        print(f'교체: [{q}]')
        print(f'  → [{new_q}]')
        item['query'] = new_q

json.dump(d, open(path,'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('저장 완료')
