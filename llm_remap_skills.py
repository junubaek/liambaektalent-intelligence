import json, time
from openai import OpenAI
from neo4j import GraphDatabase
import sys
sys.path.insert(0, '.')
from ontology_graph import CANONICAL_MAP

s = json.load(open('secrets.json', encoding='utf-8'))
client = OpenAI(api_key=s['OPENAI_API_KEY'])
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

canonical_nodes = sorted(set(CANONICAL_MAP.values()))
canonical_list = '\n'.join(canonical_nodes)

skills = json.load(open('unmapped_skills_top200.json', encoding='utf-8'))
skill_names = [s[0] for s in skills]

BATCH = 20
mapping = {}

for i in range(0, len(skill_names), BATCH):
    batch = skill_names[i:i+BATCH]
    prompt = f"""You are a skill ontology normalizer. Map each skill to the closest standard node from the list below.
Reply ONLY with JSON: {{"skill_name": "CANONICAL_NODE_or_null"}}
If no good match exists, use null.

Standard nodes:
{canonical_list}

Skills to map:
{json.dumps(batch, ensure_ascii=False)}"""
    
    resp = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role':'user','content':prompt}],
        temperature=0
    )
    text = resp.choices[0].message.content.strip()
    try:
        text = text.replace('```json','').replace('```','').strip()
        batch_map = json.loads(text)
        mapping.update(batch_map)
        print(f'Batch {i//BATCH+1}: {len([v for v in batch_map.values() if v])} mapped')
    except Exception as e:
        print(f'Batch {i//BATCH+1} error: {e}')
    time.sleep(0.5)

print(f'\nTotal mapped: {len([v for v in mapping.values() if v])} / {len(mapping)}')

# Neo4j 적용
applied = 0
with driver.session() as sess:
    for old_name, new_name in mapping.items():
        if not new_name:
            continue
        sess.run("""
            MATCH (old:Skill {name: $old_name})
            MERGE (new:Skill {name: $new_name})
            WITH old, new
            MATCH (c:Candidate)-[r]->(old)
            WITH c, r, old, new, type(r) as rel_type, properties(r) as props
            CALL apoc.create.relationship(c, rel_type, props, new) YIELD rel
            DELETE r
            WITH old
            WHERE NOT (old)--()
            DELETE old
        """, old_name=old_name, new_name=new_name)
        applied += 1

print(f'Applied to Neo4j: {applied}')

with driver.session() as sess:
    cnt = sess.run('MATCH (s:Skill) RETURN count(s) as cnt').single()['cnt']
    cnt_edge = sess.run('MATCH ()-[e]->(:Skill) RETURN count(e) as cnt').single()['cnt']
    print(f'Skill nodes: {cnt}, Edges: {cnt_edge}')

driver.close()
