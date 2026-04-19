import re

def update_ontology():
    with open("ontology_graph.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_mappings = """
    "UI 디자이너": "UX_UI_Design",
    "UIUX_Design": "UX_UI_Design",
    "인플루언서 마케터": "Content_Marketing",
    "인플루언서": "Content_Marketing",
    "테크 리크루터": "Talent_Acquisition",
    "IT 리크루터": "Talent_Acquisition",
    "엔터프라이즈 영업": "B2B영업",
    "대기업 영업": "B2B영업",
    "법인 영업": "B2B영업",
"""
    
    # We will look for CANONICAL_MAP = { and insert our new_mappings right after it.
    if "CANONICAL_MAP = {" in content:
        content = content.replace("CANONICAL_MAP = {", "CANONICAL_MAP = {" + new_mappings)
        with open("ontology_graph.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated CANONICAL_MAP successfully.")
    else:
        print("CANONICAL_MAP = { not found!")

if __name__ == "__main__":
    update_ontology()
