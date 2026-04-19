import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

from jd_compiler import api_search_v8
from ontology_graph import SKILL_CATEGORIES
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def get_candidate_skills(name):
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate {name_kr: $name})-[]->(s:Skill) RETURN s.name as skill", name=name)
        return [r['skill'] for r in res]

for q in ['Frontend', 'LLM_Serving', 'Accounting']:
    print(f"\n[{q}]")
    try:
        res = api_search_v8(prompt=q)
        cat_skills = [s.lower() for s in SKILL_CATEGORIES.get(q, [])]
        
        if isinstance(res, dict) and 'matched' in res:
            for i, r in enumerate(res['matched'][:5]):
                cand_name = r.get('name_kr', r.get('name'))
                score = r.get('score', 0)
                
                # Retrieve from Neo4j manually to show matched ones
                all_skills = get_candidate_skills(cand_name)
                matched = [s for s in all_skills if s.lower() in cat_skills]
                
                print(f"{i+1}. {cand_name} (Score: {score:.2f}) - 매칭된 스킬: {', '.join(matched)}")
    except Exception as e:
        print(f"Error fetching: {e}")
