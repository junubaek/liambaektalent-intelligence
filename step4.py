content = '''
CANONICAL_MAP.update({
    "반도체 설계": "RTL_Design",
    "반도체설계": "RTL_Design",
    "아날로그 회로": "Circuit_Design",
    "아날로그회로": "Circuit_Design",
    "회로설계": "Circuit_Design",
    "칩설계": "SoC",
    "시스템반도체": "SoC",
    "메모리반도체": "Semiconductor_Engineering",
    "공정기술": "Semiconductor_Process",
    "소자공학": "Semiconductor_Engineering",
    "검증엔지니어": "Verification_Engineer",
    "DV엔지니어": "Verification_Engineer",
    "수율관리": "Yield_Engineering",
    "품질관리": "Quality_Management",
    "QA": "Quality_Management",
    "QC": "Quality_Management",
    "FAB": "Semiconductor_Process",
    "양산기술": "Manufacturing_Process",
})
'''
with open('ontology_graph.py', 'a', encoding='utf-8') as f:
    f.write(content)
print('STEP 4 완료')
