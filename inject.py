import codecs
try:
    with codecs.open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'r', 'utf-8') as f:
        text = f.read()

    append_nodes = '''
    "PM": "Product_Manager", "Product Manager": "Product_Manager", "프로덕트매니저": "Product_Manager", "Product_Manager": "Product_Manager",
    "PO": "Product_Owner", "Product Owner": "Product_Owner", "프로덕트오너": "Product_Owner", "Product_Owner": "Product_Owner",
    "기획": "Service_Planning", "서비스기획": "Service_Planning", "Service_Planning": "Service_Planning",
    "Backend_Engineering": "Backend_Engineering", "백엔드 엔지니어링": "Backend_Engineering", "Backend Engineering": "Backend_Engineering",
    "SW_Core": "SW_Core",
    '''
    map_idx = text.find('CANONICAL_MAP: dict[str, str] = {')
    if map_idx != -1 and '"PM": "Product_Manager"' not in text:
        insert_pos = text.find('{', map_idx) + 1
        text = text[:insert_pos] + '\n' + append_nodes + text[insert_pos:]

    append_edges = '''
    ("Product_Manager", "Backend_Engineering", "related_to", 1.0),
    ("Product_Manager", "Backend", "related_to", 1.0),
    ("Product_Manager", "Data_Analysis", "used_in", 1.5),
    ("Data_Analysis", "Data_Engineering", "depends_on", 2.0),
    ("Product_Owner", "Payment_and_Settlement_System", "related_to", 2.0),
    ("Product_Manager", "Payment_and_Settlement_System", "related_to", 1.5),
    ("Product_Owner", "Product_Manager", "similar_to", 1.0),
    ("Backend_Engineering", "Payment_and_Settlement_System", "related_to", 1.0),
    '''
    edges_idx = text.find('EDGES: list[tuple[str, str, str, float]] = [')
    if edges_idx != -1 and '("Product_Manager", "Backend_Engineering"' not in text:
        insert_pos = text.find('[', edges_idx) + 1
        text = text[:insert_pos] + '\n' + append_edges + text[insert_pos:]

    with codecs.open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py', 'w', 'utf-8') as f:
        f.write(text)
    print('Successfully injected.')
except Exception as e:
    print('Error:', e)
