import sys
import re

file_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove the entire Cloud_and_DevOps_Engineering block from UNIFIED_GRAVITY_FIELD carefully
# It looks like: "Cloud_and_DevOps_Engineering": { ... },
# We can use robust string replacement or simple regex depending on formatting
pattern_cde_block = r'"Cloud_and_DevOps_Engineering":\s*\{\s*"core_attracts":\s*\{[^}]+\},\s*"synergy_attracts":\s*\{[^}]+\},\s*"repels":\s*\{[^}]+\}\s*\},?\s*'
text = re.sub(pattern_cde_block, '', text)

# 2. Modify the DevOps block to hold the merged values
devops_merged = '''"DevOps": {
        "core_attracts": {
            "Infrastructure_and_Cloud": 0.9,
            "Kubernetes": 0.8,
            "IaC": 0.7
        },
        "synergy_attracts": {
            "MSA_Architecture": 0.8,
            "Monitoring_System": 0.7,
            "CI_CD_Pipeline": 0.7
        },
        "repels": {
            "Brand_Management": -0.8,
            "UX_UI_Design": -0.7,
            "Content_Marketing": -0.8
        }
    }'''
pattern_devops_block = r'"DevOps":\s*\{\s*"core_attracts":\s*\{[^}]+\},\s*"synergy_attracts":\s*\{[^}]+\},\s*"repels":\s*\{[^}]+\}\s*\}'
text = re.sub(pattern_devops_block, devops_merged, text)

# 3. Replace all other occurrences in text (CANONICAL_MAP, EDGES, etc)
text = text.replace('"Cloud_and_DevOps_Engineering"', '"DevOps"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Done integrating DevOps nodes.')
