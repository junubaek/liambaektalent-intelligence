import sys
import os
import networkx as nx
sys.path.append(os.path.abspath('.'))
from ontology_graph import build_graph

G = build_graph()
# Convert to undirected for shortest path like Neo4j's -(s2)- (which ignores direction)
G_undirected = G.to_undirected()

s1 = 'Payment_and_Settlement_System'
s2 = 'Service_Planning'
s3 = 'Product_Manager'

def get_path_length(G, source, target):
    try:
        return nx.shortest_path_length(G, source=source, target=target)
    except nx.NetworkXNoPath:
        return 0

l1 = get_path_length(G_undirected, s1, s2)
l2 = get_path_length(G_undirected, s2, s3)
l3 = get_path_length(G_undirected, s1, s3)

b1 = 1.0 / l1 if l1 > 0 and l1 <= 4 else 0
b2 = 1.0 / l2 if l2 > 0 and l2 <= 4 else 0
b3 = 1.0 / l3 if l3 > 0 and l3 <= 4 else 0

bond_score = b1 + b2 + b3
print(f"Path lengths: s1-s2: {l1}, s2-s3: {l2}, s1-s3: {l3}")
print(f"Bond Score for this triad: {bond_score}")
