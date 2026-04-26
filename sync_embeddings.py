from neo4j import GraphDatabase

LOCAL_URI = "bolt://127.0.0.1:7687"
LOCAL_AUTH = ("neo4j", "toss1234")
AURA_URI = "neo4j+ssc://72de4959.databases.neo4j.io"
AURA_AUTH = ("72de4959", "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns")

local = GraphDatabase.driver(LOCAL_URI, auth=LOCAL_AUTH)
aura = GraphDatabase.driver(AURA_URI, auth=AURA_AUTH)

BATCH = 500

with local.session() as ls:
    print("Reading missing properties from local Neo4j...")
    rows = ls.run("""
        MATCH (c:Candidate)
        WHERE c.embedding IS NOT NULL
        RETURN c.id as id, c.embedding as emb, c.parsed_career_json as career
    """).data()

print(f"Total candidates to patch: {len(rows)}")

total = 0
for i in range(0, len(rows), BATCH):
    batch = rows[i:i+BATCH]
    with aura.session() as s:
        s.run("""
            UNWIND $rows AS r
            MATCH (c:Candidate {id: r.id})
            SET c.embedding = r.emb,
                c.parsed_career_json = r.career
        """, rows=batch)
    total += len(batch)
    print(f"Patched: {total}/{len(rows)}")

with aura.session() as s:
    print("Creating vector index 'candidate_embedding'...")
    s.run("""
        CREATE VECTOR INDEX candidate_embedding IF NOT EXISTS
        FOR (c:Candidate) ON (c.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}
    """)
    print("Index successfully created.")
    
local.close()
aura.close()
