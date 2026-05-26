from neo4j import GraphDatabase

combinations = [
    ('neo4j', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ', 'neo4j+s://deb21ee0.databases.neo4j.io'),
    ('neo4j', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ', 'neo4j+ssc://deb21ee0.databases.neo4j.io'),
    ('neo4j', 'markdown-talent', 'neo4j+ssc://deb21ee0.databases.neo4j.io'),
    ('markdown-talent', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ', 'neo4j+ssc://deb21ee0.databases.neo4j.io')
]

for user, pwd, uri in combinations:
    try:
        print(f"Trying {user} / {pwd} @ {uri}...")
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        cnt = driver.session().run('RETURN 1').single()[0]
        print(f'SUCCESS! Aura 연결 성공: {cnt} (user={user}, uri={uri})')
        driver.close()
    except Exception as e:
        print(f"FAILED: {type(e).__name__} - {e}")
        try:
            driver.close()
        except:
            pass
