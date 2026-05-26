import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Fix path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from ontology_graph import CANONICAL_MAP

syns = json.load(open('backend/synonyms.json', encoding='utf-8'))
existing_keys = set(k.lower() for k in CANONICAL_MAP.keys())

missing = []
for group in syns:
    main = group[0]
    target_node = CANONICAL_MAP.get(main)
    if not target_node:
        for term in group:
            if term in CANONICAL_MAP:
                target_node = CANONICAL_MAP[term]
                break
    if target_node:
        for term in group:
            if term.lower() not in existing_keys:
                missing.append((term, target_node))

print(f'추가할 항목: {len(missing)}개')
for term, node in missing:
    print(f'  "{term}": "{node}",')
