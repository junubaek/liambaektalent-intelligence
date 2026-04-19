import ast
import pprint

def clean_ontology_graph():
    with open('ontology_graph.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    class DictFinder(ast.NodeVisitor):
        def __init__(self):
            self.dict_node = None
        def visit_Assign(self, node):
            if len(node.targets) == 1 and getattr(node.targets[0], 'id', '') == 'CANONICAL_MAP':
                self.dict_node = node.value
            self.generic_visit(node)
        def visit_AnnAssign(self, node):
            if getattr(node.target, 'id', '') == 'CANONICAL_MAP':
                self.dict_node = node.value
            self.generic_visit(node)

    with open('ontology_graph.py', 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
        
    finder = DictFinder()
    finder.visit(tree)
    
    dict_node = finder.dict_node
    
    seen = set()
    to_delete = []
    
    for key in dict_node.keys:
        if not key: continue
        k = key.value
        if k in seen:
            to_delete.append(key.lineno)
        else:
            seen.add(k)
            
    print(f"Found {len(to_delete)} duplicate key lines to delete.")
    out_lines = []
    for i, line in enumerate(lines, 1):
        if i in to_delete:
            print(f"Deleting line {i}: {line.strip()}")
            pass
        else:
            out_lines.append(line)
            
    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
        
    print(f'Deleted {len(to_delete)} duplicate key lines.')

clean_ontology_graph()
