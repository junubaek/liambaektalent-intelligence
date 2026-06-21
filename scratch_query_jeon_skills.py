import json
import sys
import os
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"

with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

def run():
    # 1. Fetch skills from Neo4j
    q = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name_kr = '전형준' OR c.name = 'Hyeongjun Jeon' OR c.name = '전형준'
    RETURN s.name AS skill_name
    ORDER BY s.name
    """
    jeon_skills = []
    with driver.session() as session:
        res = session.run(q)
        jeon_skills = [r["skill_name"] for r in res]
    
    print("=== [1] 전형준's Skill Node Names in Neo4j ===")
    for sk in jeon_skills:
        print(f" - {sk}")
        
    # 2. Inspect ontology_graph.py CANONICAL_MAP and NODE_ALIASES for 'NPU_Kernel'
    sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
    import ontology_graph
    
    # Get all aliases in CANONICAL_MAP that map to NPU_Kernel
    canonical_aliases = [k for k, v in ontology_graph.CANONICAL_MAP.items() if v == 'NPU_Kernel']
    
    # Check NODE_ALIASES
    node_aliases_list = []
    if hasattr(ontology_graph, 'NODE_ALIASES') and 'NPU_Kernel' in ontology_graph.NODE_ALIASES:
        node_aliases_list = ontology_graph.NODE_ALIASES['NPU_Kernel']
        
    print("\n=== [2] NPU_Kernel Aliases in ontology_graph.py ===")
    print(f"CANONICAL_MAP keys mapping to 'NPU_Kernel': {canonical_aliases}")
    print(f"NODE_ALIASES['NPU_Kernel']: {node_aliases_list}")
    
    # 3. Compare
    all_current_aliases = set(canonical_aliases + node_aliases_list)
    missing = []
    # If the skill name has "kernel" or "NPU" in it and is not in all_current_aliases
    for sk in jeon_skills:
        if 'kernel' in sk.lower() or 'npu' in sk.lower():
            if sk not in all_current_aliases:
                missing.append(sk)
                
    print("\n=== [3] Comparison & Identification ===")
    print(f"Skills containing NPU/Kernel: {[sk for sk in jeon_skills if 'kernel' in sk.lower() or 'npu' in sk.lower()]}")
    print(f"Missing in NPU_Kernel aliases: {missing}")

if __name__ == "__main__":
    run()
    driver.close()
