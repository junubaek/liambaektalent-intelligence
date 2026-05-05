import os, json
from neo4j import GraphDatabase

def test_graph_match_aura():
    with open("secrets.json", "r", encoding='utf-8') as f:
        secrets = json.load(f)
    
    uri = secrets.get("NEO4J_URI")
    user = secrets.get("NEO4J_USERNAME")
    pwd = secrets.get("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    
    target_skills = ['Chief_Financial_Officer', 'cfo']
    target_id = 'f5875fc2-99aa-4605-9742-5ec93f4cd51a'
    
    with driver.session() as session:
        query = """
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' 
            RETURN DISTINCT coalesce(c.id, c.name_kr) AS id, coalesce(c.name_kr, c.name) AS name
        """
        res = session.run(query, target_skills=target_skills)
        found = False
        print("Graph Matches Found:")
        for r in res:
            if r['id'] == target_id:
                print(f"  [TARGET] {r['id']} ({r['name']})")
                found = True
            else:
                pass
        if not found:
            print("  [TARGET] NOT FOUND IN GRAPH MATCH")
    driver.close()

if __name__ == "__main__":
    test_graph_match_aura()
