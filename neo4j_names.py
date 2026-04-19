import requests
import json

url = 'http://127.0.0.1:7474/db/neo4j/tx/commit'
query = 'MATCH (c:Candidate) RETURN c.id, c.name LIMIT 5'
payload = {'statements': [{'statement': query}]}

res = requests.post(url, json=payload, auth=('neo4j', 'toss1234'))
if res.status_code == 200:
    for row in res.json()['results'][0]['data']:
        print(row['row'])
else:
    print("Failed")
