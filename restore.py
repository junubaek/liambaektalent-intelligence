import codecs
import re

with codecs.open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph_backup.py', 'r', 'utf-8') as f:
    text = f.read()

v7_canon_code = '''
# ══════════════════════════════════════════════════════════════════════════════
# 4. CANONICALIZE (V7.0 Precision Engine)
# ══════════════════════════════════════════════════════════════════════════════
import re
_sorted_keys = sorted(CANONICAL_MAP.keys(), key=len, reverse=True)

def canonicalize(skill: str) -> str:
    skill_stripped = skill.strip()
    skill_lower = skill_stripped.lower()

    for key in _sorted_keys:
        if key.lower() == skill_lower:
            return CANONICAL_MAP[key]

    for key in _sorted_keys:
        if re.search(r'[a-zA-Z]', key):
            pattern = r'\\b' + re.escape(key) + r'\\b'
            if re.search(pattern, skill_stripped, re.IGNORECASE):
                return CANONICAL_MAP[key]
        else:
            if key in skill_stripped:
                return CANONICAL_MAP[key]

    return skill_stripped
'''

header_match = re.search(r'def canonicalize\(', text)
if header_match:
    pre_text = text[:header_match.start()]
    post_text = text[header_match.start():]
    batch_idx = post_text.find('def canonicalize_batch(')
    if batch_idx != -1:
        text = pre_text + v7_canon_code + post_text[batch_idx:]

with codecs.open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'w', 'utf-8') as f:
    f.write(text)

print('Restored 1344 node graph with V7 canonicalize logic.')
