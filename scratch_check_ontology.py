import sys; sys.stdout.reconfigure(encoding='utf-8')
from ontology_graph import UNIFIED_GRAVITY_FIELD, CANONICAL_MAP

# V3에서 추가된 것들 있는지 확인
check = [
    'C_CPP', 'Database_Management', 'Blockchain_Ecosystem',
    'Manufacturing_Digital_Transformation', 'FinTech',
    'Backend_Java', 'High_Performance_Computing',
    'Tax_Accounting', 'IR_Management',
    'Talent_Acquisition', 'Organizational_Development',
    'Performance_Marketing', 'Brand_Management',
]
print('=== Gravity Field 상태 ===')
for node in check:
    has = node in UNIFIED_GRAVITY_FIELD
    has_core = bool(UNIFIED_GRAVITY_FIELD.get(node, {}).get('core_attracts'))
    print(f'{node}: {"있음" if has else "없음"} | core: {has_core}')

print()
print('=== CANONICAL_MAP 한국어 키워드 ===')
kr_keys = ['클라우드 영업', '해외영업', '백엔드개발', '재무회계', '채용담당']
for k in kr_keys:
    print(f'{k}: {CANONICAL_MAP.get(k, "없음")}')
