import sys
try:
    from app.engine.neo4j_snapper import Neo4jCandidateSnapper
except ImportError:
    pass

jd_tendency = {'Tech': 0, 'Sales': 0, 'Product': 0, 'Business': 0}
jd_nodes_list = [
    {'name': 'Payment_and_Settlement_System', 'weight': 2.0, 'is_core': False},
    {'name': 'Product_Manager', 'weight': 4.0, 'is_core': True},
    {'name': 'Product_Owner', 'weight': 4.0, 'is_core': True},
    {'name': 'Service_Planning', 'weight': 2.0, 'is_core': False},
    {'name': 'Corporate_Accounting', 'weight': -1.0, 'is_core': False}
]

uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
user = "neo4j"
password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"

from neo4j import GraphDatabase

print("Connecting to DB...")
driver = GraphDatabase.driver(uri, auth=(user, password))

query = """
    UNWIND $jd_nodes AS jd_node
    MATCH (c:Candidate) WHERE id(c) IS NOT NULL
    
    // 이 쿼리는 단순 검증용. 실제 엔진의 Cypher를 복붙
    MATCH (c:Candidate {id: $candidate_id})-[r:HAS_SKILL]->(cand_skill:Skill)
    MATCH p = shortestPath((cand_skill)-[:RELATED_TO|DEPENDS_ON|USED_IN*0..2]-(target:Skill {name: jd_node.name}))
    WHERE p IS NOT NULL
    WITH c, target AS jd_node_db, jd_node, cand_skill, length(p) AS distance, r.weight AS c_weight
    
    WITH c, jd_node, cand_skill, distance, c_weight,
         (cand_skill.mass * 10) / (cand_skill.degree + 12.0) AS safe_mass 
    
    WITH c, jd_node, cand_skill, distance, c_weight, safe_mass,
         CASE WHEN jd_node.is_core THEN 4.0 ELSE 1.0 END AS core_boost
         
    WITH c, jd_node,
         max((safe_mass * c_weight * jd_node.weight * core_boost) / (1.0 + distance)) AS max_gravity_for_this_jd_node
         
    WITH c, sum(max_gravity_for_this_jd_node) AS raw_gravity
    RETURN c.name AS name, raw_gravity
"""

with driver.session() as session:
    kim_id = "31f22567-1b6f-817a-a763-f718d9d40fbf"
    result = session.run(query, jd_nodes=jd_nodes_list, candidate_id=kim_id)
    records = [record.data() for record in result]
    print("Direct Neo4j Result:", records)

driver.close()
