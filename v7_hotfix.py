import re

with open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix 1: Add 'Corporate' to Corporate_Strategy so it passes the trap test
import_point = '''"전략": "Corporate_Strategy",'''
code = code.replace(import_point, '''"Corporate": "Corporate_Strategy",\n    "전략": "Corporate_Strategy",''')

# Fix 2: Add missing edges for Customer_Experience and EPC_PM
edge_injection_point = '''    ("Sensor_Fusion",    "Hardware_Engineering","related_to",1.0),
    ("Sensor_Fusion",    "Computer_Vision",    "related_to",1.0),
}'''
new_edges = '''    ("Sensor_Fusion",    "Hardware_Engineering","related_to",1.0),
    ("Sensor_Fusion",    "Computer_Vision",    "related_to",1.0),

    # ── V7.1 Patches: Isolated Node Fixes ──────────────────────────────────
    ("Customer_Experience","Business_Operations","related_to",1.0),
    ("Customer_Experience","Marketing_Planning", "related_to",1.0),
    ("EPC_PM",           "Product_Manager",    "similar_to",1.0),
    ("EPC_PM",           "Hardware_Engineering","related_to",1.0),
}'''
code = code.replace(edge_injection_point, new_edges)

with open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Hotfixes applied to V7.")
