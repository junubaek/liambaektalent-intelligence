from neo4j import GraphDatabase

def main():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as s:
        res = s.run('MATCH (c:Candidate {name:"최호진"})-[r]->(s:Skill) RETURN s.name, type(r)')
        edges = [(rec["s.name"], rec["type(r)"]) for rec in res]
        print(edges)
        
    driver.close()

if __name__ == '__main__':
    main()
