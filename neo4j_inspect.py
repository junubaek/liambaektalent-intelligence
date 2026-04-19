import requests

url = 'http://127.0.0.1:7474/db/neo4j/tx/commit'
query = 'MATCH (c:Candidate) RETURN keys(c), [(k) IN keys(c) | c[k]] LIMIT 1'
payload = {'statements': [{'statement': query}]}

res = requests.post(url, json=payload, auth=('neo4j', 'toss1234'))
if res.status_code == 200:
    data = res.json()['results'][0]['data'][0]['row']
    
    props = data[0]
    values = data[1]
    
    for i in range(len(props)):
        print(f"{props[i]}: {str(values[i])[:100]}")
else:
    print("FAILED")
