with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    text = f.read()

addition = '''    "Android": "Android_Development",
    "안드로이드": "Android_Development",
    "Android_Development": "Android_Development",
'''
text = text.replace('CANONICAL_MAP: dict[str, str] = {', 'CANONICAL_MAP: dict[str, str] = {\n' + addition)
with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
