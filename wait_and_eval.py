import time
import os
import subprocess
from neo4j import GraphDatabase

def check_count():
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN count(c)")
        count = res.single()[0]
    driver.close()
    return count

print("Waiting for embeddings to reach ~4500...")
while True:
    try:
        cnt = check_count()
        print(f"Current embedding count: {cnt}", flush=True)
        if cnt >= 4200: 
            print("Target reached! Running evaluations...")
            break
    except Exception as e:
        print(f"Error checking count: {e}")
    time.sleep(15)
    
print("Running test_real_4q.py...")
with open("test_4q_vector.log", "w", encoding="utf-8") as f:
    subprocess.run(["python", "test_real_4q.py"], stdout=f, stderr=f, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    
print("Running run_real_evaluate_v3.py...")
with open("eval_vector.log", "w", encoding="utf-8") as f:
    subprocess.run(["python", "run_real_evaluate_v3.py"], stdout=f, stderr=f, env=dict(os.environ, PYTHONIOENCODING="utf-8"))

print("All evaluations done.")
