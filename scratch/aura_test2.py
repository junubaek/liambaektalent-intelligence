from neo4j import GraphDatabase
driver = GraphDatabase.driver(
    'neo4j+ssc://deb21ee0.databases.neo4j.io',
    auth=('neo4j', 'markdown-talent')
)
cnt = driver.session().run('RETURN 1').single()[0]
print(f'Aura 연결 성공 (markdown-talent): {cnt}')
driver.close()
