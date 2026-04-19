def update_ontology():
    with open("ontology_graph.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 콘텐츠 기획자 매핑 수정 (Content_Marketing_Strategy -> Content_Marketing)
    # Be careful not to replace the relationship edges if any, just the exact canonical map lines
    # Actually, the user says parse_jd_to_json returns Content_Marketing_Strategy for "콘텐츠 기획자".
    # We will just replace all `"Content_Marketing_Strategy",` with `"Content_Marketing",` in CANONICAL_MAP? 
    # Or just replace specific strings. Let's do simple replaces:
    content = content.replace('"콘텐츠 기획": "Content_Marketing_Strategy",', '"콘텐츠 기획": "Content_Marketing",')
    content = content.replace('"콘텐츠 기획자": "Content_Marketing_Strategy",', '"콘텐츠 기획자": "Content_Marketing",')
    
    # Also in case it maps other things:
    content = content.replace('"콘텐츠 마케팅 전략": "Content_Marketing_Strategy",', '"콘텐츠 마케팅 전략": "Content_Marketing",')
    content = content.replace('"브랜드 스토리텔링": "Content_Marketing_Strategy",', '"브랜드 스토리텔링": "Content_Marketing",')

    # 2. SEO 마케터 및 조직문화 담당자 추가
    new_mappings = """
    "SEO": "Performance_Marketing",
    "SEO 마케터": "Performance_Marketing",
    "검색엔진최적화": "Performance_Marketing",
    "조직문화 담당자": "Organizational_Development",
    "콘텐츠 기획자": "Content_Marketing",
"""
    
    if "CANONICAL_MAP: dict[str, str] = {" in content:
        content = content.replace("CANONICAL_MAP: dict[str, str] = {", "CANONICAL_MAP: dict[str, str] = {" + new_mappings)
        with open("ontology_graph.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated CANONICAL_MAP successfully.")
    else:
        print("CANONICAL_MAP not found!")

if __name__ == "__main__":
    update_ontology()
