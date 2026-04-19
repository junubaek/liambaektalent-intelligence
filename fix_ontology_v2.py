import sys
import re

file_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'^UNIFIED_GRAVITY_FIELD\s*=\s*\{', 'EXPLICIT_GRAVITY_FIELD = {', text, flags=re.MULTILINE)

auto_gen_code = '''
# -------------------------------------------------------------------------
# ⚙️ [핵심] UNIFIED_GRAVITY_FIELD 스마트 동적 병합기 (Smart Auto-Generator)
# -------------------------------------------------------------------------
UNIFIED_GRAVITY_FIELD = EXPLICIT_GRAVITY_FIELD.copy()

# Antigravity의 우려(노이즈 폭발)를 완벽히 해결한 필터링 로직
for src, tgt, rel, weight in EDGES:
    if src not in UNIFIED_GRAVITY_FIELD:
        UNIFIED_GRAVITY_FIELD[src] = {"core_attracts": {}, "synergy_attracts": {}, "repels": {}}
    
    # 🛡️ 방어 로직: 가중치가 1.5 이상인 '확실한 시너지'만 중력장에 편입!
    if weight >= 1.5:
        # 하드코딩(Explicit)으로 미리 정의해둔 정교한 세팅이 있다면 그게 무조건 우선! (덮어쓰기 방지)
        if tgt not in UNIFIED_GRAVITY_FIELD[src].get("synergy_attracts", {}) and \\
           tgt not in UNIFIED_GRAVITY_FIELD[src].get("core_attracts", {}) and \\
           tgt not in UNIFIED_GRAVITY_FIELD[src].get("repels", {}):
            
            UNIFIED_GRAVITY_FIELD[src]["synergy_attracts"][tgt] = weight
'''

if 'EXPLICIT_GRAVITY_FIELD = {' in text and 'Smart Auto-Generator' not in text:
    text += '\n' + auto_gen_code
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated ontology_graph.py successfully!')
else:
    print('Failed to find or already updated.')
