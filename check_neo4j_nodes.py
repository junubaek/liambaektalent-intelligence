from neo4j import GraphDatabase
import json

def check_nodes():
    uri = "neo4j+ssc://72de4959.databases.neo4j.io"
    user = "72de4959"
    password = "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns"
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    test_skills = ["Kubernetes", "Kafka", "MLOps", "Data_Pipeline_Construction", "Treasury_Management", "ERP", "Python", "Backend_Python"]
    
    results = {}
    with driver.session() as session:
        for s in test_skills:
            res = session.run("MATCH (n:Skill {name: $name}) RETURN count(n) as count", name=s).single()
            results[s] = res["count"]
            
            # If not found, try case-insensitive or partial match
            if res["count"] == 0:
                res_any = session.run("MATCH (n:Skill) WHERE n.name CONTAINS $name RETURN n.name LIMIT 3", name=s)
                results[s + "_suggestions"] = [r["n.name"] for r in res_any]
                
    driver.close()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check_nodes()
