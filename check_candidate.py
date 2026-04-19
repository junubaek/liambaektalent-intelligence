from neo4j import GraphDatabase
from collections import Counter

def run():
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate {name_kr: '윤석훈'})-[r]->(s:Skill) RETURN type(r) as action, s.name as skill")
        docs = res.data()
        
    print(f"Total edges: {len(docs)}")
    actions = Counter(d["action"] for d in docs)
    print("Actions:", actions.most_common())
    skills = Counter(d["skill"] for d in docs)
    print("Top Skills:", skills.most_common(10))

if __name__ == "__main__":
    run()
