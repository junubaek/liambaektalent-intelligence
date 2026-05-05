import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 추가할 엣지들
new_edges = """
    # --- Product_Owner 시너지 강화 (2026-05-06) ---
    ("Product_Owner", "Product_Service_Planning", "related_to", 2.5),
    ("Product_Owner", "Data_Driven_Decision", "related_to", 1.5),
    ("Product_Owner", "User_Research", "related_to", 1.3),
"""

# 기준 라인 (공백 포함 정확히 일치해야 함)
target = '    ("Product_Owner",   "Business_Development",        "related_to", 1.0),'

if target not in content:
    print("❌ 기준 라인을 찾지 못했습니다. ontology_graph.py 구조를 확인해주세요.")
    # 공백 차이일 수 있으므로 유연하게 찾기 시도
    import re
    match = re.search(r'\("Product_Owner",\s+"Business_Development",\s+"related_to",\s+1\.0\),', content)
    if match:
        target = match.group(0)
        print(f"  → 유연한 검색으로 기준 라인 발견: {target}")
    else:
        sys.exit(1)

# 이미 추가됐는지 확인
if 'Product_Owner 시너지 강화 (2026-05-06)' in content:
    print("⚠️  이미 추가된 엣지입니다. 중복 실행 방지.")
    sys.exit(0)

new_content = content.replace(
    target,
    target + new_edges
)

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ ontology_graph.py 엣지 추가 완료")
print()
print("추가된 엣지:")
print("  Product_Owner → Product_Service_Planning  2.5")
print("  Product_Owner → Data_Driven_Decision      1.5")
print("  Product_Owner → User_Research             1.3")
print()

# 검증: 추가됐는지 확인
with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    verify = f.read()

checks = [
    '("Product_Owner", "Product_Service_Planning", "related_to", 2.5)',
    '("Product_Owner", "Data_Driven_Decision", "related_to", 1.5)',
    '("Product_Owner", "User_Research", "related_to", 1.3)',
]
for check in checks:
    status = "✅" if check in verify else "❌"
    print(f"  {status} {check}")
