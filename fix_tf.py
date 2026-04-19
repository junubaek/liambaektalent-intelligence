import sys
file_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"Terraform": "DevOps"', '"Terraform": "IaC"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Terraform mapped to IaC.')
