import sys
import re

file_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find UNIFIED_GRAVITY_FIELD = {
match = re.search(r'UNIFIED_GRAVITY_FIELD\s*=\s*\{', text)
if match:
    insert_pos = match.end()
    
    code_to_insert = '''
    "DevOps": {
        "core_attracts": {
            "Cloud_and_DevOps_Engineering": 0.9,
            "Infrastructure_and_Cloud": 0.8,
            "Kubernetes": 0.8
        },
        "synergy_attracts": {
            "MSA_Architecture": 0.8,
            "Monitoring_System": 0.7,
            "IaC": 0.8,
            "CI_CD_Pipeline": 0.7
        },
        "repels": {
            "Brand_Management": -0.8,
            "UX_UI_Design": -0.7,
            "Content_Marketing": -0.8
        }
    },

    "Cloud_and_DevOps_Engineering": {
        "core_attracts": {
            "Infrastructure_and_Cloud": 0.9,
            "Kubernetes": 0.8,
            "IaC": 0.7
        },
        "synergy_attracts": {
            "MSA_Architecture": 0.8,
            "DevOps": 0.9,
            "Monitoring_System": 0.7
        },
        "repels": {
            "Brand_Management": -0.8,
            "UX_UI_Design": -0.7
        }
    },
'''
    new_text = text[:insert_pos] + '\n' + code_to_insert + text[insert_pos:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Inserted successfully.')
else:
    print('Not found.')
