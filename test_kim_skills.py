import sys
uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
user = "neo4j"
password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"

from neo4j import GraphDatabase
driver = GraphDatabase.driver(uri, auth=(user, password))

query = """
MATCH (c:Candidate {id: '31f22567-1b6f-817a-a763-f718d9d40fbf'})-[r:HAS_SKILL]->(s:Skill)
RETURN s.name AS skill, r.raw_weight AS weight
"""

with driver.session() as session:
    result = session.run(query)
    records = [record.data() for record in result]
    print("Kim Wan-hee's NEW Skills in DB:", records)

driver.close()
