import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

# We need to access the logic inside api_search_v9 before it returns
# I'll copy the core logic or just increase the slice in a local version

from jd_compiler import api_search_v9

# I'll modify the source of jd_compiler.py temporarily to return 300 results
# Or I can just check the results of a search for his ID specifically? 
# No, I want to see his rank.

def find_rank(target_id):
    import json, time, math
    from jd_compiler import api_search_v9
    
    # Run search
    res = api_search_v9("General Affairs Manager")
    # Wait, api_search_v9 returns the result dict.
    # The 'matched' list is limited to 50.
    
    # I'll use a hack: search for his name specifically to see if he comes up?
    # No, that won't tell me the rank for "General Affairs Manager".
    
    # Let's check why his score is low.
    # I'll check his Neo4j node again.
    
    from neo4j import GraphDatabase
    secrets = json.load(open('secrets.json'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    
    with driver.session() as session:
        # Check if he has skills that match "General Affairs"
        res = session.run("""
            MATCH (c:Candidate {id: $id})-[:HAS_SKILL]->(s:Skill)
            RETURN s.name as skill
        """, id=target_id)
        skills = [r['skill'] for r in res]
        print(f"Skills for {target_id}: {skills}")
        
    driver.close()

find_rank('db752f0f-0f1a-437c-a09d-43c20442ab7b')
