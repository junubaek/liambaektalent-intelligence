with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace 'repels': [] with 'repels': {}
# We also have to handle double quote versions if any
code = code.replace("'repels': []", "'repels': {}")
code = code.replace('"repels": []', '"repels": {}')

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Fixed repels definition in ontology_graph.py.")
