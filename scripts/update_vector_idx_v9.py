from neo4j import GraphDatabase

d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','toss1234'))
q1 = "DROP INDEX resume_embeddings IF EXISTS"
q2 = """
CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (e:Experience_Chunk)
ON (e.embedding)
OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}}
"""
with d.session() as s: 
    s.run(q1)
    s.run(q2)
print('chunk_embeddings Vector Index Created successfully!')
d.close()
