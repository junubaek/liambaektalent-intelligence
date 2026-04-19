from neo4j import GraphDatabase

def peek():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    
    query = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WITH c, collect({skill: s.name, action: type(r)}) as skills
    WHERE size(skills) >= 6
    RETURN c.name_kr as name, skills
    ORDER BY c.created_at DESC
    LIMIT 3
    """
    
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            name = record["name"]
            skills = record["skills"]
            print(f"\n[{name}]님의 새로운 스킬 트랙:")
            for s in skills:
                # Format to look nice
                action_map = {
                    'BUILT': '개발/구축', 'DESIGNED': '설계', 'MANAGED': '관리',
                    'ANALYZED': '분석/연구', 'SUPPORTED': '지원/협업', 'NEGOTIATED': '협상',
                    'GREW': '성장/마케팅', 'LAUNCHED': '출시/배포', 'LED': '리딩/총괄',
                    'OPTIMIZED': '최적화', 'PLANNED': '기획', 'EXECUTED': '실행'
                }
                action = action_map.get(s['action'], s['action'])
                print(f"  🔹 [{action}] -> {s['skill']}")
    
    driver.close()

if __name__ == '__main__':
    peek()
