from neo4j import GraphDatabase

def test():
    d = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j','toss1234'))
    res = d.execute_query("MATCH (c:Candidate)-[r]->(s) WHERE c.name CONTAINS '홍기재' OR c.name_kr = '홍기재' RETURN c.name_kr, type(r), s.name")
    print(res)

if __name__ == '__main__':
    test()
