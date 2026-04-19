import sys
from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
auth = ("neo4j", "toss1234")

# MERGE Mapping specified by the user
ghost_map = {
    "Android": "Android_Development",
    "브랜드마케팅": "Brand_Management",
    "Litigation": "Legal_Compliance"
}

def merge_ghosts():
    driver = GraphDatabase.driver(uri, auth=auth)
    
    with driver.session() as session:
        for ghost, target in ghost_map.items():
            print(f"Merging '{ghost}' -> '{target}'...")
            
            query = """
            MATCH (g:Skill {name: $ghost})
            MERGE (t:Skill {name: $target})
            WITH g, t
            MATCH (c:Candidate)-[r]->(g)
            RETURN c.id AS cid, type(r) AS r_type, r.weight AS r_weight, g, t
            """
            result = session.run(query, ghost=ghost, target=target)
            edges_to_create = [record.data() for record in result]
            
            for edge in edges_to_create:
                cid = edge['cid']
                r_type = edge['r_type']
                r_weight = edge['r_weight'] if edge['r_weight'] is not None else 1.0
                
                merge_q = f"""
                MATCH (c:Candidate {{id: $cid}})
                MERGE (t:Skill {{name: $target}})
                MERGE (c)-[new_r:{r_type}]->(t)
                SET new_r.weight = $r_weight
                """
                session.run(merge_q, cid=cid, target=target, r_weight=r_weight)
                
            session.run("MATCH (g:Skill {name: $ghost}) DETACH DELETE g", ghost=ghost)

    print("✅ Final 3 ghost nodes merged and deleted.")
    driver.close()

if __name__ == "__main__":
    merge_ghosts()
