from neo4j import GraphDatabase
import json

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def merge_nodes(session, source, target):
    # Get all distinct actions
    res = session.run(f"MATCH (c:Candidate)-[r]->(s:Skill {{name: '{source}'}}) RETURN DISTINCT type(r) as action")
    actions = [r['action'] for r in res]
    
    for action in actions:
        # Create new relationships to target
        session.run(f"""
            MATCH (c:Candidate)-[r:{action}]->(s:Skill {{name: '{source}'}})
            MERGE (t:Skill {{name: '{target}'}})
            MERGE (c)-[new_r:{action}]->(t)
        """)
        
    # Delete source node and its relationships
    session.run(f"""
        MATCH (s:Skill {{name: '{source}'}})
        DETACH DELETE s
    """)
    print(f"✅ Merged '{source}' into '{target}'")

with driver.session() as session:
    print("=== 1. 해외영업 통합 ===")
    merge_nodes(session, "해외영업", "Global_Sales_and_Marketing")
    
    print("\n=== 2. 조직문화 통합 ===")
    res = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE s.name IN ['Organizational_Development', 'Corporate_Culture_Branding']
        RETURN s.name as name, count(r) as cnt
    """)
    counts = {rec['name']: rec['cnt'] for rec in res}
    od_cnt = counts.get('Organizational_Development', 0)
    ccb_cnt = counts.get('Corporate_Culture_Branding', 0)
    
    print(f"Organizational_Development edges: {od_cnt}")
    print(f"Corporate_Culture_Branding edges: {ccb_cnt}")
    
    if od_cnt >= ccb_cnt:
        target = "Organizational_Development"
        source = "Corporate_Culture_Branding"
    else:
        target = "Corporate_Culture_Branding"
        source = "Organizational_Development"
        
    print(f"-> Merging '{source}' into '{target}'")
    merge_nodes(session, source, target)
    
    with open("org_target.txt", "w", encoding="utf-8") as f:
        f.write(target)
