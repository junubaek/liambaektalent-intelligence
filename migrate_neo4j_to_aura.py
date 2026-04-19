import sys
from neo4j import GraphDatabase
from collections import defaultdict
import time

LOCAL_URI = "bolt://127.0.0.1:7687"
LOCAL_AUTH = ("neo4j", "toss1234")

AURA_URI = "neo4j+ssc://eb435464.databases.neo4j.io"
AURA_AUTH = ("eb435464", "EEdwBC6Yk45YKNYtYH8Aw9VQrglbXvxFLDX6EUwAH1s")

BATCH_SIZE = 500

def migrate():
    local_driver = GraphDatabase.driver(LOCAL_URI, auth=LOCAL_AUTH)
    aura_driver = GraphDatabase.driver(AURA_URI, auth=AURA_AUTH)

    # 1. Clean AuraDB
    print("Cleaning AuraDB before migration...")
    with aura_driver.session() as session:
        session.run("MATCH (n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 10000 ROWS")
        
    print("AuraDB cleaned.")

    print("\n[1/4] Fetching all nodes from Local Neo4j...")
    nodes = []
    with local_driver.session() as session:
        result = session.run("MATCH (n) RETURN id(n) AS old_id, labels(n) AS labels, properties(n) AS props")
        for record in result:
            nodes.append({
                "old_id": record["old_id"],
                "labels": list(record["labels"]),
                "props": dict(record["props"])
            })
            
    print(f">> Found {len(nodes)} nodes. Grouping by labels...")
    
    nodes_by_labels = defaultdict(list)
    for n in nodes:
        lbl = ":".join(sorted(n["labels"]))
        nodes_by_labels[lbl].append(n)
        
    print("\n[2/4] Uploading nodes to AuraDB in batches...")
    start_time = time.time()
    with aura_driver.session() as session:
        # Create temporary index
        session.run("CREATE INDEX _old_id_idx IF NOT EXISTS FOR (n:MigrationTemp) ON (n._old_id)")
        
        for lbl_str, n_list in nodes_by_labels.items():
            print(f"  -> Uploading {len(n_list)} nodes with labels [ {lbl_str} ] ...")
            cypher_lbl = ":" + lbl_str + ":MigrationTemp" if lbl_str else ":MigrationTemp"
            
            for i in range(0, len(n_list), BATCH_SIZE):
                batch = n_list[i:i+BATCH_SIZE]
                params = []
                for n in batch:
                    props = n["props"]
                    props["_old_id"] = n["old_id"]
                    params.append({"props": props})
                query = f"UNWIND $batch AS row CREATE (n{cypher_lbl}) SET n = row.props"
                session.run(query, parameters={"batch": params})
    print(f">> Done uploading nodes (Elapsed: {time.time() - start_time:.2f}s).")


    print("\n[3/4] Fetching all edges from Local Neo4j...")
    edges = []
    with local_driver.session() as session:
        result = session.run("MATCH (a)-[r]->(b) RETURN id(a) AS start_id, id(b) AS end_id, type(r) AS type, properties(r) AS props")
        for record in result:
            edges.append({
                "start": record["start_id"],
                "end": record["end_id"],
                "type": record["type"],
                "props": dict(record["props"])
            })

    print(f">> Found {len(edges)} edges. Grouping by type...")
    edges_by_type = defaultdict(list)
    for e in edges:
        edges_by_type[e["type"]].append(e)

    print("\n[4/4] Uploading edges to AuraDB in batches...")
    start_time = time.time()
    with aura_driver.session() as session:
        for rel_type, e_list in edges_by_type.items():
            print(f"  -> Uploading {len(e_list)} edges of type [ {rel_type} ] ...")
            for i in range(0, len(e_list), BATCH_SIZE):
                batch = []
                for e in e_list[i:i+BATCH_SIZE]:
                    batch.append({
                        "start": e["start"],
                        "end": e["end"],
                        "props": e["props"]
                    })
                query = f"""
                UNWIND $batch AS row
                MATCH (a:MigrationTemp {{_old_id: row.start}}), (b:MigrationTemp {{_old_id: row.end}})
                CREATE (a)-[r:{rel_type}]->(b)
                SET r = row.props
                """
                session.run(query, parameters={"batch": batch})

        print("\nCleaning up temporary indices and labels...")
        session.run("MATCH (n:MigrationTemp) CALL { WITH n REMOVE n._old_id REMOVE n:MigrationTemp } IN TRANSACTIONS OF 10000 ROWS")
        session.run("DROP INDEX _old_id_idx IF EXISTS")
    print(f">> Done uploading edges (Elapsed: {time.time() - start_time:.2f}s).")

    print("\n================== Verification ==================")
    with aura_driver.session() as session:
        c = session.run("MATCH (c:Candidate) RETURN count(c) as n").single()["n"]
        sk = session.run("MATCH (s:Skill) RETURN count(s) as n").single()["n"]
        e = session.run("MATCH ()-[r]->() RETURN count(r) as n").single()["n"]
        total_nodes = session.run("MATCH (n) RETURN count(n) as n").single()["n"]
        
        print(f"✅ FINAL AuraDB Stats -> Total Nodes: {total_nodes}")
        print(f"                      -> Candidates: {c}")
        print(f"                      -> Skills: {sk}")
        print(f"                      -> Total Edges: {e}")

    local_driver.close()
    aura_driver.close()

if __name__ == '__main__':
    migrate()
