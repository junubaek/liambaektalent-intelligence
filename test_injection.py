import codecs
with codecs.open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'r', 'utf-8') as f:
    text = f.read()

append_nodes = '''
    "Financial System": "Payment_and_Settlement_System", "정산 시스템": "Payment_and_Settlement_System", "정산": "Payment_and_Settlement_System", "정산 데이터": "Payment_and_Settlement_System",
    "Project Manager(PM)": "Product_Manager", "pm": "Product_Manager", "Product Manager(PM)": "Product_Manager",
    "Product Owner(PO)": "Product_Owner", "po": "Product_Owner",
    "시스템 기획": "Service_Planning", "시스템 설계": "Service_Planning", "시스템 구축": "Service_Planning",
'''
map_idx = text.find('CANONICAL_MAP: dict[str, str] = {')
if map_idx != -1 and '"정산 시스템": "Payment_and_Settlement_System"' not in text:
    insert_pos = text.find('{', map_idx) + 1
    text = text[:insert_pos] + '\n' + append_nodes + text[insert_pos:]

with codecs.open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'w', 'utf-8') as f:
    f.write(text)
print('Successfully injected string aliases.')
