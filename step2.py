content = '''
UNIFIED_GRAVITY_FIELD.update({
    "Android_Development": {
        "core_attracts": {"Mobile_Application_Development": 0.9},
        "repels": {"Frontend_Development": -0.1}
    },
    "Mobile_Application_Development": {
        "core_attracts": {"Android_Development": 0.8},
    },
    "iOS_Development": {
        "core_attracts": {"Mobile_Application_Development": 0.9},
        "repels": {"Android_Development": -0.1}
    },
})
'''
with open('ontology_graph.py', 'a', encoding='utf-8') as f:
    f.write(content)
print('STEP 2 완료')
