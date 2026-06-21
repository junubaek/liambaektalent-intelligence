import json, sys
from neo4j import GraphDatabase, exceptions
sys.stdout.reconfigure(encoding='utf-8')

s = json.load(open('secrets.json'))
uri = s['NEO4J_URI'].strip()
username = s['NEO4J_USERNAME'].strip()
password = s['NEO4J_PASSWORD'].strip()

def try_connect(uri, username, password, encrypted=True):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password), encrypted=encrypted)
        with driver.session() as session:
            result = session.run('RETURN 1 AS n').single()
            print('Neo4j 연결 성공 (encrypted=' + str(encrypted) + '):', result['n'])
        driver.close()
        return True
    except exceptions.AuthError as e:
        print('AuthError (encrypted=' + str(encrypted) + '):', e)
        return False
    except Exception as e:
        print('Other error (encrypted=' + str(encrypted) + '):', e)
        return False

# First try with original URI (may include +s) and encryption
if not try_connect(uri, username, password, encrypted=True):
    # Fallback: replace +s with no encryption, ensure uri uses neo4j://
    fallback_uri = uri.replace('neo4j+s://', 'neo4j://')
    try_connect(fallback_uri, username, password, encrypted=False)
