from neo4j import GraphDatabase

def fix_kim_edges():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        # First check duplicate candidate nodes
        res_cand = session.run("MATCH (c:Candidate) WHERE c.name_kr='김대용' RETURN collect(c) as nodes")
        c_nodes = res_cand.single()['nodes']
        if len(c_nodes) > 1:
            print(f"Deleting {len(c_nodes)-1} duplicate Candidate nodes for 김대용...")
            session.run("""
            MATCH (c:Candidate) WHERE c.name_kr='김대용'
            WITH collect(c) as nodes
            UNWIND nodes[1..] as dup
            DETACH DELETE dup
            """)
            
        print("Cleaning duplicate relations...")
        session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.name_kr = '김대용'
        WITH c, s.name as s_name, type(r) as rtype, collect(r) as rels
        WHERE size(rels) > 1
        UNWIND rels[1..] as dup
        DELETE dup
        """)
        
        # Skill duplication checkout across the DB might be necessary, but this solves his edges.
        
        q_count = """
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.name_kr = '김대용'
        RETURN count(r) AS total_edges
        """
        res = session.run(q_count)
        for r in res:
            print(f"✅ 실행 후 김대용의 남은 엣지 총 개수: {r['total_edges']}")
            
    driver.close()

if __name__ == '__main__':
    fix_kim_edges()
