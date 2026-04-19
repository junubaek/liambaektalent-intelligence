import json
import codecs

data = json.load(codecs.open('temp_500_candidates.json', encoding='utf-8-sig'))
s = set()
for c in data['results']:
    props = c.get('properties', {})
    rc = props.get('Role Cluster', {}).get('multi_select', [])
    for item in rc:
        s.add(item['name'])

print(list(s))
