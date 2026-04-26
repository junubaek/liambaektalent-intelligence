import sys; sys.stdout.reconfigure(encoding='utf-8')
from ontology_graph import CANONICAL_MAP, UNIFIED_GRAVITY_FIELD

for k in ['cloud 영업', 'IT영업', 'IT 영업', '솔루션 영업', '클라우드 영업', 'SaaS 영업', 'B2B IT 영업']:
    print(f"{k} -> {CANONICAL_MAP.get(k, '없음')}")

ts = UNIFIED_GRAVITY_FIELD.get('Technical_Sales', {})
print('Technical_Sales core_attracts:', ts.get('core_attracts', {}))
