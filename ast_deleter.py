import ast

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
tree = ast.parse("".join(lines))

dict_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AnnAssign) and getattr(node.target, 'id', '') == 'CANONICAL_MAP':
        dict_node = node.value
        break

if not dict_node:
    print("CANONICAL_MAP dict not found!")
    exit(1)

seen_keys = set()
to_delete = set()

# values might be dictionaries ? No CANONICAL_MAP has string keys.
for key in dict_node.keys:
    if key is None: continue
    if isinstance(key, ast.Constant):
        k = key.value
        if k in seen_keys:
            to_delete.add(key.lineno)
        else:
            seen_keys.add(k)
            
print(f"Duplicates found: {len(to_delete)}")
out_lines = []
for i, line in enumerate(lines, 1):
    if i in to_delete:
        pass # Skipping line
    else:
        out_lines.append(line)

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)
    
print(f"Lines deleted: {len(to_delete)}")
