from neo4j import GraphDatabase

d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','toss1234'))
query = """
CREATE VECTOR INDEX resume_embeddings IF NOT EXISTS
FOR (c:Candidate)
ON (c.embedding)
OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}}
"""
with d.session() as s: 
    s.run(query)
print('Vector Index Created successfully!')
d.close()
