content = '''
UNIFIED_GRAVITY_FIELD.update({
    "Product_Manager": {
        "core_attracts": {
            "Product_Service_Planning": 0.9,
            "Agile_Methodology": 0.8,
            "Business_Model_Planning": 0.7,
            "UX_UI_Design": 0.5,
        },
        "repels": {
            "Tax_Accounting": -0.3,
            "Financial_Accounting": -0.2,
        }
    },
})
'''
with open('ontology_graph.py', 'a', encoding='utf-8') as f:
    f.write(content)
print('STEP 3 완료')
