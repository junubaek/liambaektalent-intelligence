content = '''
UNIFIED_GRAVITY_FIELD.update({
    "Data_Science": {
        "core_attracts": {
            "Machine_Learning": 0.9,
            "Deep_Learning": 0.7,
            "Data_Analysis": 0.7,
        },
        "repels": {"Data_Engineering": -0.15}
    },
    "Data_Engineering": {
        "core_attracts": {
            "Data_Pipeline_Construction": 0.9,
            "Big_Data_Processing": 0.8,
            "Data_Warehouse_Architecture": 0.8,
        },
        "repels": {"Data_Science": -0.15}
    },
})
'''
with open('ontology_graph.py', 'a', encoding='utf-8') as f:
    f.write(content)
print('STEP 1 완료')
