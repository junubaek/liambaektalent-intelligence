import json

path = r'C:\Users\cazam\Downloads\안티그래비티_온톨로지 사전\local_ontology.json'
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    projects = data.get('projects', [])
    concepts = data.get('concepts', [])

    print(f"Total projects: {len(projects)}")
    print(f"Total concepts: {len(concepts)}")

    proj_with_pat = sum(1 for p in projects if 'patterns' in p and p['patterns'])
    con_with_pat = sum(1 for c in concepts if 'patterns' in c and c['patterns'])

    print(f"Projects with 'patterns' field: {sum(1 for p in projects if 'patterns' in p)}")
    print(f"Concepts with 'patterns' field: {sum(1 for c in concepts if 'patterns' in c)}")
    
    print(f"Projects with NON-EMPTY patterns: {proj_with_pat}")
    print(f"Concepts with NON-EMPTY patterns: {con_with_pat}")
    
    # Also check if there's any other field named similarly
    if len(projects) > 0:
        print("Sample project keys:", list(projects[0].keys()))
    if len(concepts) > 0:
        print("Sample concept keys:", list(concepts[0].keys()))

except Exception as e:
    print('Error:', e)
