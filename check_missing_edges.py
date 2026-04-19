from neo4j import GraphDatabase

def check_edges():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        q = """
        MATCH (c:Candidate)-[r:BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED|NEGOTIATED|GREW|LAUNCHED|LED|OPTIMIZED|PLANNED|EXECUTED]->(s:Skill)
        WHERE c.name_kr IN ['홍기재', '오원교', '전예찬', '이수진']
        RETURN c.name_kr, count(r) AS edge_count
        ORDER BY edge_count DESC
        """
        res = session.run(q)
        print("--- Edge Counts ---")
        for record in res:
            print(f"{record['c.name_kr']}: {record['edge_count']}")
    driver.close()

if __name__ == '__main__':
    check_edges()
