from neo4j import GraphDatabase
uri = "neo4j+ssc://72de4959.databases.neo4j.io"
driver = GraphDatabase.driver(uri, auth=("72de4959", "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns"))
with driver.session() as s:
    s.run("""
    CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
    FOR (e:Experience_Chunk) ON (e.embedding)
    OPTIONS {indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
    }}
    """)
    print("Chunk index created.")
driver.close()
