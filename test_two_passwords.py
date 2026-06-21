import json, sys
from neo4j import GraphDatabase, exceptions
sys.stdout.reconfigure(encoding='utf-8')

# Load base config (URI & username) from secrets.json
s = json.load(open('secrets.json'))
uri = s['NEO4J_URI'].strip()
username = s['NEO4J_USERNAME'].strip()

passwords = [
    "pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ",
    "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns"
]

def try_connect(pwd, encrypted=True):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, pwd), encrypted=encrypted)
        with driver.session() as session:
            result = session.run('RETURN 1 AS n').single()
            print(f"✅ 연결 성공 (encrypted={encrypted}) 비밀번호: {pwd[:6]}... ", result['n'])
        driver.close()
        return True
    except exceptions.AuthError as e:
        print(f"❌ AuthError (encrypted={encrypted}) 비밀번호: {pwd[:6]}... ", e)
        return False
    except Exception as e:
        print(f"❌ 기타 오류 (encrypted={encrypted}) 비밀번호: {pwd[:6]}... ", e)
        return False

print('=== 암호화된 연결 시도 ===')
for pwd in passwords:
    if try_connect(pwd, encrypted=True):
        break
else:
    print('--- 암호화된 연결 모두 실패, 비암호화 시도 ---')
    for pwd in passwords:
        if try_connect(pwd, encrypted=False):
            break
