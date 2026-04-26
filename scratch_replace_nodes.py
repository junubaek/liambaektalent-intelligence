with open('ontology_graph.py', 'r', encoding='utf-8', errors='surrogateescape') as f:
    content = f.read()

replacements = {
    "'B2B영업'": "'B2B_Sales'",
    "\"B2B영업\"": "\"B2B_Sales\"",
    "'Sales_Core'": "'Global_Sales_and_Marketing'",
    "\"Sales_Core\"": "\"Global_Sales_and_Marketing\"",
    "'HR_Core'": "'HR_Strategic_Planning'",
    "\"HR_Core\"": "\"HR_Strategic_Planning\"",
    "'SW_Software'": "'Backend_Engineering'",
    "\"SW_Software\"": "\"Backend_Engineering\"",
    "'영업기획'": "'Sales_Planning'",
    "\"영업기획\"": "\"Sales_Planning\"",
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('ontology_graph.py', 'w', encoding='utf-8', errors='surrogateescape') as f:
    f.write(content)
print('교체 완료')
