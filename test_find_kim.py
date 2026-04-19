import sys
try:
    from app.engine.neo4j_snapper import Neo4jCandidateSnapper
except ImportError:
    pass

uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
user = "neo4j"
password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"

from neo4j import GraphDatabase
driver = GraphDatabase.driver(uri, auth=(user, password))

query = """
MATCH (c:Candidate) WHERE c.name CONTAINS '김완희'
RETURN c.id AS id, c.name AS name
"""

with driver.session() as session:
    result = session.run(query)
    records = [record.data() for record in result]
    print("Kim Wan-hee in Neo4j:", records)

driver.close()
