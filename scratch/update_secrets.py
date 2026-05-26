import json
with open('secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)

# Note: We verified earlier that the username for this instance is deb21ee0, not neo4j.
# Using neo4j+s as requested by user.
s['NEO4J_URI'] = 'neo4j+s://deb21ee0.databases.neo4j.io'
s['NEO4J_USERNAME'] = 'deb21ee0'
s['NEO4J_PASSWORD'] = 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ'

with open('secrets.json', 'w', encoding='utf-8') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
print('secrets.json 업데이트 완료')
