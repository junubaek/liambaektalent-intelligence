
import re
import sys

def get_stats():
    with open('ontology_graph.py', 'r', encoding='utf-8') as f:
        content = f.read()
    edges = re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*([\d.]+)\)', content)
    nodes = set()
    for s, d, r, w in edges:
        nodes.add(s)
        nodes.add(d)
    return len(nodes), len(edges)

if __name__ == "__main__":
    n, e = get_stats()
    print(f"Nodes: {n}, Edges: {e}")
