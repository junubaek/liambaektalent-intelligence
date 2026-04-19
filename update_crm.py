with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"CRM마케팅"', '"CRM_Marketing"')
text = text.replace("'CRM마케팅'", "'CRM_Marketing'")

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
