import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ontology_graph

vault_dir = os.path.join(os.path.dirname(__file__), '..', 'obsidian_vault')
if os.path.exists(vault_dir):
    shutil.rmtree(vault_dir)

os.makedirs(os.path.join(vault_dir, "Skills"))

template = '''---
aliases: {aliases}
category: "Domain"
---

# {name}

이 문서는 **[[{name}]]** 직무/도메인(스킬/경험)에 대한 온톨로지 정의입니다.

## 의존성 (Depends On / 강력한 필요 요소)
{depends_on_body}

## 일부 포함 / 사용 분야 (Part Of / Used In)
{part_of_body}

## 유사 / 연관 궤도 (Related To / Similar)
{related_to_body}

'''

# 추출
all_nodes = set(ontology_graph.CANONICAL_MAP.values())
for s, t, r, w in ontology_graph.EDGES:
    all_nodes.add(s)
    all_nodes.add(t)

for node in all_nodes:
    aliases = []
    for alias, canon in ontology_graph.CANONICAL_MAP.items():
        if canon == node:
            aliases.append(alias)
            
    depends_on = []
    part_of = []
    related_to = []
    
    for s, t, rel, w in ontology_graph.EDGES:
        if s == node:
            if rel == "depends_on":
                depends_on.append(t)
            elif rel in ["part_of", "used_in"]:
                part_of.append(t)
            else:
                related_to.append(t)
                
    # 양방향 related_to 처리 (A related_to B 이면 B related_to A 이기도 하므로 시각화를 위해 반대쪽도 채워줌)
    for s, t, rel, w in ontology_graph.EDGES:
        if t == node and rel in ["related_to", "similar_to"]:
            if s not in related_to:
                related_to.append(s)
                
    aliases_str = "[" + ", ".join([f'"{a}"' for a in aliases]) + "]"
    
    depends_on_body = "\n".join([f"- [[{d}]]" for d in depends_on]) if depends_on else "- 없음"
    part_of_body = "\n".join([f"- [[{p}]]" for p in part_of]) if part_of else "- 없음"
    related_to_body = "\n".join([f"- [[{r}]]" for r in related_to]) if related_to else "- 없음"

    content = template.format(
        name=node,
        aliases=aliases_str,
        depends_on_body=depends_on_body,
        part_of_body=part_of_body,
        related_to_body=related_to_body
    )
    
    safe_name = str(node).replace("/", "_")
    filepath = os.path.join(vault_dir, "Skills", f"{safe_name}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ Generated {len(all_nodes)} unified Obsidian logic nodes in '{vault_dir}/Skills' from ontology_graph.py!")
