import os
import sys
import json
import codecs

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.graph_engine.obsidian_parser import ObsidianParser
from app.graph_engine.core_graph import SkillGraphEngine

def load_all_raw_skills(filepath):
    try:
        with codecs.open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

    results = data.get('results', [])
    all_raw_skills = set()
    
    for c in results:
        props = c.get('properties', {})
        for prop_name, prop_data in props.items():
            prop_type = prop_data.get('type')
            if any(keyword in prop_name.lower() for keyword in ['skill', 'tech', 'stack', '분야', '경험', '역량', 'sector']):
                if prop_type == 'multi_select':
                    for item in prop_data.get('multi_select', []):
                        name = item['name'].strip()
                        if name:
                            all_raw_skills.add(name)
                elif prop_type == 'rich_text':
                    text_content = "".join([t.get('plain_text', '') for t in prop_data.get('rich_text', [])])
                    if ',' in text_content:
                        for part in text_content.split(','):
                            name = part.strip()
                            if name:
                                all_raw_skills.add(name)
    return list(all_raw_skills)

def run_auto_discovery():
    vault_path = os.path.join(os.path.dirname(__file__), '..', 'obsidian_vault')
    parser = ObsidianParser(vault_path)
    nodes = parser.parse_all_nodes()
    
    engine = SkillGraphEngine()
    engine.canonical_map = parser.canonical_map
    engine.build_graph(nodes)
    
    canonical_dict = engine.get_all_nodes_with_aliases()
    canonical_keys_lower = [k.lower() for k in canonical_dict.keys()]
    
    candidates_path = os.path.join(os.path.dirname(__file__), '..', 'temp_candidates.json')
    raw_skills = load_all_raw_skills(candidates_path)
    
    print(f"Total Unique Raw Skills in Candidates: {len(raw_skills)}")
    
    unmapped_skills = []
    
    for raw in raw_skills:
        raw_lower = raw.lower()
        # 부분 일치가 있는지 확인 (예: '마케팅 기획' 이 '마케팅'에 매칭되는지)
        # 보다 엄격히 하기 위해 정확한 매칭이 없으면 unmapped 로 편입
        is_mapped = False
        for c_key in canonical_keys_lower:
            if c_key in raw_lower:
                is_mapped = True
                break
                
        if not is_mapped:
            unmapped_skills.append(raw)
            
    # 특수문자나 너무 긴 문장은 필터링 (간단한 스킬 위주로 통과)
    def is_valid_skill(s):
        if len(s) > 20: return False
        if '"' in s or '\\' in s or ':' in s: return False
        return True

    final_unmapped = [s for s in unmapped_skills if is_valid_skill(s)]
    print(f"Discovered New Unknown Skills: {len(final_unmapped)}")
    
    # Discovery 폴더 생성
    discovery_dir = os.path.join(vault_path, "Skills", "Discovery")
    if not os.path.exists(discovery_dir):
        os.makedirs(discovery_dir)
        
    created_count = 0
    for skill in final_unmapped:
        safe_name = skill.replace("/", "_").replace("&", "_").replace("?", "")
        filepath = os.path.join(discovery_dir, f"{safe_name}.md")
        
        # 이미 존재하는 노드인지 확인 (Discovery 폴더 안)
        if not os.path.exists(filepath):
            template = f"""---
type: skill
domain: Discovery
aliases:
  - {skill}
mass: auto

depends_on: []
related_to: []
part_of: []
used_in: []
similar_to: []
---

# {skill}

자동 생성된 미확인 스킬 노드입니다.
옵시디언 그래프 뷰에서 다른 항성(Core Node)과 선을 연결해 주세요!
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(template)
            created_count += 1
            
    print(f"Success! Generated {created_count} New Markdown Nodes in '{discovery_dir}'.")
    print("대표님은 이제 옵시디언을 열어 Discovery 폴더의 노드들을 메인 그래프에 드래그&드롭으로 연결하시면 됩니다.")

if __name__ == "__main__":
    run_auto_discovery()
