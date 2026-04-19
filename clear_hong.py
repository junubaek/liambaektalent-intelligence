from neo4j import GraphDatabase

def clean_and_check():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        session.run("MATCH (c:Candidate)-[r]->() WHERE c.name_kr='홍기재' DELETE r")
        print("Deleted old edges for 홍기재.")
    driver.close()

if __name__ == '__main__':
    clean_and_check()
