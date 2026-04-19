from neo4j import GraphDatabase

def fix_neo4j_names():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        # 여기어때 -> 김다혜
        res1 = session.run("MATCH (c:Candidate) WHERE c.name_kr CONTAINS '여기어때' SET c.name_kr = '김다혜', c.name = '김다혜' RETURN c.id")
        print("여기어때 -> 김다혜:", [r["c.id"] for r in res1])
        
        # 자동화제(콘텐츠PD) -> 송영
        res2 = session.run("MATCH (c:Candidate) WHERE c.name_kr CONTAINS '자동화제(콘텐츠PD)' SET c.name_kr = '송영', c.name = '송영' RETURN c.id")
        print("자동화제(콘텐츠PD) -> 송영:", [r["c.id"] for r in res2])
        
        # 자동화제(자동화 제어) -> 미상
        res3 = session.run("MATCH (c:Candidate) WHERE c.name_kr CONTAINS '자동화제(자동화' SET c.name_kr = '미상_자동화개발', c.name = '미상_자동화개발' RETURN c.id")
        print("자동화제(자동화 제어) -> 미상:", [r["c.id"] for r in res3])
    driver.close()

if __name__ == '__main__':
    fix_neo4j_names()
