import os
import sys
import json
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)

neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

with open(CACHE_FILE, "r", encoding="utf-8") as f:
    cands = json.load(f)

for c in cands:
    name = c.get('name_kr', '')
    cid = c.get('id')
    careers = c.get('parsed_career_json')
    if not careers or not isinstance(careers, list): continue

    if name == '장혜선':
        new_careers = []
        seen = set()
        for x in careers:
            comp = x.get('company', '')
            if comp == '㈜코리아세븐':
                if comp in seen: continue
                seen.add(comp)
            new_careers.append(x)
        c['parsed_career_json'] = new_careers

    elif name == '임동혁':
        new_careers = []
        seen = set()
        for x in careers:
            comp = x.get('company', '')
            if comp == 'Samsung Electronics':
                if comp in seen: continue
                seen.add(comp)
            new_careers.append(x)
        c['parsed_career_json'] = new_careers

    elif name == '박현덕':
        samsung_item = None
        new_careers = []
        for x in careers:
            comp = x.get('company', '')
            if comp in ['삼성 반도체', 'Samsung Electronics']:
                if not samsung_item:
                    samsung_item = x
                    samsung_item['company'] = 'Samsung Electronics'
                    new_careers.append(samsung_item)
                else:
                    p1 = samsung_item.get('period', '')
                    p2 = x.get('period', '')
                    if len(p2) > len(p1): 
                        samsung_item['period'] = p2
            else:
                new_careers.append(x)
        c['parsed_career_json'] = new_careers

with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(cands, f, ensure_ascii=False, indent=2)

print("Manual merge in cache applied.")

with driver.session() as session:
    for c in cands:
        name = c.get('name_kr', '')
        if name in ['장혜선', '임동혁', '박현덕']:
            cid = c.get('id')
            careers_str = json.dumps(c.get('parsed_career_json'), ensure_ascii=False)
            session.run("MATCH (n:Candidate {id: $id}) SET n.parsed_career_json = $data", id=cid, data=careers_str)

print("Neo4j parity updated.")
driver.close()
