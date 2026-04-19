import re

# 1. Update jd_compiler.py
with open("jd_compiler.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add ACTION_WEIGHTS constant
if "ACTION_WEIGHTS" not in text:
    text = text.replace("EXECUTIVE_NODES = {", "ACTION_WEIGHTS = {\n    'MIGRATED': 1.7,\n    'DEPLOYED': 1.6,\n    'RESOLVED': 1.5,\n    'CLOSED': 1.8,\n    'DRAFTED': 1.3\n}\n\nEXECUTIVE_NODES = {")

# Update Cypher queries matching relationships
# Old: MATCH (c:Candidate)-[r:BUILT|...|EXECUTED]->(s:Skill)
old_rel = "BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED|NEGOTIATED|GREW|LAUNCHED|LED|OPTIMIZED|PLANNED|EXECUTED"
new_rel = "BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED|NEGOTIATED|GREW|LAUNCHED|LED|OPTIMIZED|PLANNED|EXECUTED|MIGRATED|DEPLOYED|RESOLVED|CLOSED|DRAFTED"
text = text.replace(f"[r:{old_rel}]", f"[r:{new_rel}]")

# Update collecting mechanism
old_return = "RETURN c.name_kr AS name, collect(DISTINCT s.name) AS skills"
new_return = "RETURN c.name_kr AS name, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills"
text = text.replace(old_return, new_return)

# Update score calculation
calc_old = """        for skill in candidate_edges:

            # 2. dict.get()을 사용하여 KeyError 원천 차단

            if skill in field.get("core_attracts", {}):

                core_bonus += field.get("core_attracts").get(skill, 0)

                matched_edges += 1

            elif skill in field.get("synergy_attracts", {}):

                synergy_bonus += field.get("synergy_attracts").get(skill, 0)

                matched_edges += 1

            elif skill in field.get("repels", {}):"""

calc_new = """        for edge in candidate_edges:
            if isinstance(edge, dict):
                skill = edge['skill']
                action = edge['action']
            else:
                skill = edge
                action = "MANAGED"
                
            weight_mult = ACTION_WEIGHTS.get(action, 1.0)
            
            # 2. dict.get()을 사용하여 KeyError 원천 차단
            if skill in field.get("core_attracts", {}):
                core_bonus += field.get("core_attracts").get(skill, 0) * weight_mult
                matched_edges += 1
            elif skill in field.get("synergy_attracts", {}):
                synergy_bonus += field.get("synergy_attracts").get(skill, 0) * weight_mult
                matched_edges += 1
            elif skill in field.get("repels", {}):"""
            
text = text.replace(calc_old, calc_new)

# Update freeform skill calculation
ff_old = """        freeform_cnt = sum(1 for edge in cand_edges if edge.lower() in freeform_skills)"""
ff_new = """        freeform_cnt = sum(1 for edge in cand_edges if (edge['skill'].lower() if isinstance(edge, dict) else edge.lower()) in freeform_skills)"""
text = text.replace(ff_old, ff_new)

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(text)


# 2. Update dynamic_parser_v2.py
parser_rule = """
[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.
"""

with open("dynamic_parser_v2.py", "r", encoding="utf-8") as f:
    v2_text = f.read()
    
if "[고유명사 원형 보존 원칙]" not in v2_text:
    v2_text = v2_text.replace("[문장 분석 Few-Shot 예시]", parser_rule + "\n[문장 분석 Few-Shot 예시]")
    
# Add new actions to Enum
if "MIGRATED" not in v2_text:
    v2_text = v2_text.replace("SUPPORTED = \"SUPPORTED\"", "SUPPORTED = \"SUPPORTED\"\n    MIGRATED = \"MIGRATED\"\n    DEPLOYED = \"DEPLOYED\"\n    RESOLVED = \"RESOLVED\"\n    CLOSED = \"CLOSED\"\n    DRAFTED = \"DRAFTED\"")
    
with open("dynamic_parser_v2.py", "w", encoding="utf-8") as f:
    f.write(v2_text)

# 3. Update dynamic_parser.py (v1)
with open("dynamic_parser.py", "r", encoding="utf-8") as f:
    v1_text = f.read()

if "[고유명사 원형 보존 원칙]" not in v1_text:
    v1_text = v1_text.replace("[특별 추출 카테고리]", parser_rule + "\n[특별 추출 카테고리]")
    
with open("dynamic_parser.py", "w", encoding="utf-8") as f:
    f.write(v1_text)

print("SUCCESS")
