from neo4j import GraphDatabase

def check_kim():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        # Check candidate nodes for 김대용
        res1 = session.run('''
        MATCH (c:Candidate)
        WHERE c.name_kr = "김대용"
        RETURN count(c) as cand_count, collect(c.id) as ids
        ''')
        r = res1.single()
        print(f"Number of '김대용' Candiate nodes: {r['cand_count']}")
        print(f"IDs: {r['ids']}")
        
        # Look at the duplicate edges logic again
        res2 = session.run('''
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.name_kr = "김대용"
        RETURN type(r), s.name, count(r) as cnt
        ORDER BY cnt DESC LIMIT 10
        ''')
        print("Top 10 edges:")
        for edge in res2:
            print(f"{edge['type(r)']} -> {edge['s.name']} : {edge['cnt']}")

    driver.close()

if __name__ == '__main__':
    check_kim()
