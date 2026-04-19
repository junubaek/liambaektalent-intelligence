import os
import sys
import json
import codecs

# 루트 디렉토리를 경로에 추가하여 app 모듈 임포트 가능하도록 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.graph_engine.obsidian_parser import ObsidianParser
from app.graph_engine.core_graph import SkillGraphEngine
from app.engine.resume_snap import CandidateSnapper

def load_sample_candidates(filepath='temp_candidates.json', limit=20):
    try:
        with codecs.open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

    results = data.get('results', [])
    candidates_list = []
    
    for c in results[:limit]:
        props = c.get('properties', {})
        
        # Name
        name = "Unknown"
        if "이름" in props:
            name_prop = props["이름"].get("title", [])
            if name_prop:
                name = name_prop[0].get("plain_text", "Unknown")
        elif "Name" in props:
            name_prop = props["Name"].get("title", [])
            if name_prop:
                name = name_prop[0].get("plain_text", "Unknown")

        # Skills (다중 필드 통합)
        skills = []
        for prop_name, prop_data in props.items():
            prop_type = prop_data.get('type')
            if any(keyword in prop_name.lower() for keyword in ['skill', 'tech', 'stack', '분야', '경험', '역량', 'sector']):
                if prop_type == 'multi_select':
                    skills.extend([item['name'] for item in prop_data.get('multi_select', [])])
                elif prop_type == 'rich_text':
                    text_content = "".join([t.get('plain_text', '') for t in prop_data.get('rich_text', [])])
                    if ',' in text_content:
                        skills.extend([x.strip() for x in text_content.split(',') if x.strip()])
                        
        if skills:
            candidates_list.append({
                "name": name,
                "raw_skills": list(set(skills))
            })
        
        if len(candidates_list) >= limit:
            break
            
    return candidates_list

def run_mvp_test():
    # 1. 옵시디언 뼈대(Ontology) 파싱
    vault_path = os.path.join(os.path.dirname(__file__), '..', 'obsidian_vault')
    parser = ObsidianParser(vault_path)
    nodes = parser.parse_all_nodes()
    
    # 2. Graph 엔진 구축
    engine = SkillGraphEngine()
    engine.canonical_map = parser.canonical_map
    engine.build_graph(nodes)
    
    # 3. 매핑 엔진(Antigravity) 준비
    snapper = CandidateSnapper(engine)
    
    # 4. 후보자 샘플 로드 (20건)
    candidates_path = os.path.join(os.path.dirname(__file__), '..', 'temp_candidates.json')
    candidates = load_sample_candidates(candidates_path, limit=20)
    print(f"✅ Loaded {len(candidates)} Candidates for testing.")
    
    # 5. JD 테스트 시나리오
    jds = [
        "신사업 발굴과 전략 기획, 재무 분석 역량이 필요한 인재",
        "데이터를 바탕으로 퍼포먼스 마케팅을 기획할 수 있는 사람",
        "AI 런타임 백엔드 엔지니어링 역량"
    ]
    
    print("\n" + "="*50)
    print("🚀 Antigravity 엔진 매칭 테스트 시작 (MVP)")
    print("="*50)
    
    for jd in jds:
        print(f"\n📝 [JD (Job Description)]: '{jd}'")
        mapped_nodes = snapper.extract_and_map_skills([jd])
        
        matches = snapper.rank_candidates_for_jd(jd, candidates)
        if not matches:
             print("❌ 매칭되는 인재가 없습니다.")
        else:
             print("\n🏆 [Top 5 추천 인재]")
             for i, m in enumerate(matches[:5], 1):
                 # matched_nodes is now a dictionary: {node_id: weight}
                 matched = ", ".join([f"{k}(wt:{v:.1f})" for k, v in m['matched_nodes'].items()])
                 print(f"{i}. {m['name']} (Score: {m['score']:.1f})")
                 print(f"   ㄴ보유 항성(Vector): {matched}")
                 print(f"   ㄴ원물 스킬: {', '.join(m['raw_skills'][:7])}...")

if __name__ == "__main__":
    run_mvp_test()
