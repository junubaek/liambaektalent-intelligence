from neo4j import GraphDatabase

def main():
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        session.run("MATCH (c:Candidate) WHERE c.total_years = 0.0 SET c.seniority = '미상'")
        
        j = session.run("MATCH (c:Candidate) WHERE c.seniority='Junior' RETURN count(c) as cnt").single()['cnt']
        m = session.run("MATCH (c:Candidate) WHERE c.seniority='Middle' RETURN count(c) as cnt").single()['cnt']
        s = session.run("MATCH (c:Candidate) WHERE c.seniority='Senior' RETURN count(c) as cnt").single()['cnt']
        u = session.run("MATCH (c:Candidate) WHERE c.seniority='미상' RETURN count(c) as cnt").single()['cnt']
        
        print(f"Junior: {j}")
        print(f"Middle: {m}")
        print(f"Senior: {s}")
        print(f"미상: {u}")

if __name__ == "__main__":
    main()
