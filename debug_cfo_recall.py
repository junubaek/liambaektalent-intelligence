import os, json, sqlite3
from neo4j import GraphDatabase
from openai import OpenAI

def debug():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    target_id = 'f5875fc2-99aa-4605-9742-5ec93f4cd51a'
    prompt = 'cfo'

    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    
    with driver.session() as session:
        # 1. Inspect Properties
        print("--- Inspecting AuraDB Node ---")
        res = session.run('MATCH (c:Candidate {id: $id}) RETURN properties(c)', id=target_id)
        record = res.single()
        if record:
            props = record[0]
            print(f"Found: {props.get('name_kr')} (ID: {props.get('id')})")
            print(f"Has Embedding: {'embedding' in props}")
        else:
            print("Target candidate NOT FOUND in AuraDB.")

        # 2. Vector Recall Check
        print("\n--- Vector Recall Check ---")
        client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
        emb_res = client.embeddings.create(input=[prompt], model='text-embedding-3-small')
        query_vector = emb_res.data[0].embedding
        
        # Note: We use queryNodes for vector search
        res_v = session.run('''
            CALL db.index.vector.queryNodes("candidate_embedding", 100, $queryVector)
            YIELD node AS c, score
            RETURN c.id AS id, c.name_kr as name, score
        ''', queryVector=query_vector)
        
        found_v = False
        for r in res_v:
            if r['id'] == target_id:
                print(f"FOUND in Vector top 100! Score: {r['score']}")
                found_v = True
                break
        if not found_v:
            print("NOT found in Vector top 100.")

        # 3. Graph Recall Check
        print("\n--- Graph Recall Check ---")
        target_skills = ['Chief_Financial_Officer', 'cfo']
        res_g = session.run('''
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE s.name IN $target_skills AND type(r) <> "USED_AS_TEMP"
            RETURN DISTINCT c.id AS id, c.name_kr AS name
        ''', target_skills=target_skills)
        
        found_g = False
        for r in res_g:
            if r['id'] == target_id:
                print(f"FOUND in Graph match! ID: {r['id']}")
                found_g = True
                break
        if not found_g:
            print("NOT found in Graph Skill match.")

    driver.close()

if __name__ == "__main__":
    debug()
