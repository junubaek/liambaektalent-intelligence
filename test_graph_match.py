import os
from neo4j import GraphDatabase

def test_graph_match():
    uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    user = os.environ.get('NEO4J_USERNAME', 'neo4j')
    pwd = os.environ.get('NEO4J_PASSWORD', 'toss1234')
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
        for r in res:
            if r['id'] == target_id:
                print(f"FOUND IN GRAPH MATCH: {r['id']} ({r['name']})")
                found = True
        if not found:
            print("NOT FOUND IN GRAPH MATCH")
    driver.close()

if __name__ == "__main__":
    test_graph_match()
