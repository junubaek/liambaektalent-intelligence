import ast

class DictDuplicateChecker(ast.NodeVisitor):
    def __init__(self):
        self.duplicates = {}

    def visit_Dict(self, node):
        seen = {}
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                k = key.value
                v = value.value if isinstance(value, ast.Constant) else ast.unparse(value)
                if k in seen:
                    self.duplicates[k] = {'first': seen[k], 'second': v}
                seen[k] = v
        self.generic_visit(node)

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

checker = DictDuplicateChecker()
checker.visit(tree)

with open('dup_results_utf8.txt', 'w', encoding='utf-8') as out:
    out.write(f"중복 키 총 {len(checker.duplicates)}개:\n")
    for k, v in checker.duplicates.items():
        out.write(f"  '{k}': {v['first']} -> {v['second']}\n")
