import os
import sys
import json
import codecs

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.graph_engine.core_graph import SkillGraphEngine
from app.engine.resume_snap import CandidateSnapper
import ontology_graph

def load_candidates():
    candidates_path = os.path.join(os.path.dirname(__file__), '..', 'temp_500_candidates.json')
    try:
        with codecs.open(candidates_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading candidates: {e}")
        return []

    results = data.get('results', [])
    candidates_list = []
    
    for c in results[:500]: # Scan a healthy pool
        props = c.get('properties', {})
        
        name = "Unknown"
        if "이름" in props and props["이름"].get("title"):
             name = props["이름"]["title"][0].get("plain_text", "Unknown")
        elif "Name" in props and props["Name"].get("title"):
             name = props["Name"]["title"][0].get("plain_text", "Unknown")

        skills = []
        for prop_name, prop_data in props.items():
            prop_type = prop_data.get('type')
            if any(k in prop_name.lower() for k in ['skill', 'tech', 'stack', '분야', '경험', '역량', 'sector']):
                if prop_type == 'multi_select':
                    skills.extend([item['name'] for item in prop_data.get('multi_select', [])])
                elif prop_type == 'rich_text':
                    text_content = "".join([t.get('plain_text', '') for t in prop_data.get('rich_text', [])])
                    if ',' in text_content:
                        skills.extend([x.strip() for x in text_content.split(',') if x.strip()])
                        
        main_sectors = []
        if "Main Sectors" in props and props["Main Sectors"].get("multi_select"):
            main_sectors = [item["name"] for item in props["Main Sectors"].get("multi_select", [])]
            
        experience_summary = ""
        if "Experience Summary" in props and props["Experience Summary"].get("rich_text"):
            experience_summary = " ".join([t.get('plain_text', '') for t in props["Experience Summary"].get("rich_text", [])])

        if skills:
            candidates_list.append({
                "name": name,
                "raw_skills": list(set(skills)),
                "raw_text": " ".join(set(skills)).lower(),
                "main_sectors": main_sectors,
                "experience_summary": experience_summary
            })
            
    return candidates_list

def rank_keyword_control(jd_keywords, candidates):
    """
    Control Group: 순수 다중 키워드 매칭
    JD에 나온 단어(리스트 단위)가 후보자의 이력서/스킬텍스트에 몇 개 들어있는지만 카운트 (Frequency 기반 없음, Orbit 없음)
    """
    results = []
    for cand in candidates:
        score = 0
        matches = []
        for kw in jd_keywords:
            if kw.lower() in cand["raw_text"]:
                score += 1
                matches.append(kw)
                
        if score > 0:
            results.append({
                "name": cand["name"],
                "score": score * 10.0, # Scale to align visually with gravity scale differences somewhat
                "matched_nodes": matches,
                "raw_skills": cand["raw_skills"]
            })
            
    # 높은 점수 순 정렬
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

import ontology_graph

def get_engine():
    parsed_nodes = []
    
    # Gather all node canonical names
    all_node_names = set(ontology_graph.CANONICAL_MAP.values())
    for s, t, rel, w in ontology_graph.EDGES:
        all_node_names.add(s)
        all_node_names.add(t)
        
    for name in all_node_names:
        node_info = {
            "id": name,
            "aliases": [],
            "category": "Domain", 
            "depends_on": [],
            "related_to": [],
            "part_of": [],
            "used_in": [],
            "similar_to": []
        }
        for alias, canon in ontology_graph.CANONICAL_MAP.items():
            if canon == name:
                node_info["aliases"].append(alias)
                
        for s, t, rel, w in ontology_graph.EDGES:
            if s == name:
                if rel in node_info and isinstance(node_info[rel], list):
                    node_info[rel].append(t)
                else:
                    node_info["related_to"].append(t)
        parsed_nodes.append(node_info)
        
    engine = SkillGraphEngine()
    engine.canonical_map = ontology_graph.CANONICAL_MAP
    engine.build_graph(parsed_nodes)
    
    print("\n--- ENGINE LOAD DEBUG ---")
    print(f"Nodes in G: {engine.graph.number_of_nodes()}")
    print(f"DevOps in G.nodes: {'DevOps' in engine.graph.nodes}")
    print(f"Canonicalize('인프라_Cloud'): {ontology_graph.canonicalize('인프라_Cloud')}")
    print("-------------------------\n")
    
    return engine

def run_ab_test():
    engine = get_engine()
    snapper = CandidateSnapper(engine)
    candidates = load_candidates()
    
    jds = [
        {
            "id": "JD_4",
            "title": "클라우드 서비스 인프라 구축",
            "query": "AWS, Docker 환경에서 쿠버네티스 배포 경험, DevOps 도입",
            "keywords": ["AWS", "Docker", "DevOps", "쿠버네티스", "인프라"],
            "domain": "IT/Tech",
            "core_intents": {"DevOps": 3.0, "인프라": 2.0},
            "tendency": {"Tech": 0.9, "Product": 0.1}
        },
        {
            "id": "JD_5",
            "title": "온라인 이커머스 그로스 마케팅",
            "query": "퍼포먼스 마케팅 전문, 그로스 해킹, CRM 캠페인 운영, 커머스 거래액 극대화 경험",
            "keywords": ["마케팅", "커머스", "퍼포먼스", "그로스", "CRM"],
            "domain": "Commerce",
            "core_intents": {"퍼포먼스 마케팅": 3.0, "CRM": 2.0},
            "tendency": {"Sales": 0.8, "Strategy": 0.2}
        },
        {
            "id": "JD_6",
            "title": "글로벌 B2B 반도체 영업",
            "query": "해외 거래선 발굴 및 B2B 반도체 장비 영업, 기술 제안",
            "keywords": ["반도체", "B2B", "영업", "해외", "기술영업"],
            "domain": "Semiconductor",
            "core_intents": {"반도체": 4.0, "B2B": 2.0},
            "tendency": {"Sales": 0.7, "Tech": 0.2, "Strategy": 0.1}
        },
        {
            "id": "JD_7",
            "title": "인공지능 추천 알고리즘 MLOps 파이프라인 개발",
            "query": "오픈소스 추천 시스템 아키텍처 구축 및 딥러닝 모델 서빙 파이프라인 경험, MLOps 기반으로 모델 배포 모델 자동화 구축",
            "keywords": ["추천", "파이프라인", "모델", "MLOps", "딥러닝", "서빙"],
            "domain": "AI/Data",
            "core_intents": {"MLOps": 5.0, "MachineLearning": 3.0},
            "tendency": {"Tech": 0.9, "Business": 0.1}
        }
    ]
    
    output_path = os.path.join(os.path.dirname(__file__), '..', 'evaluation_report.md')
    
    with codecs.open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🧪 A/B Testing Report: Keyword vs Gravity Engine\n\n")
        f.write("> **지시사항 (For Recruiter):** 본 문서는 블라인드 테스트 폼입니다. 동일한 JD에 대해 `Method A`와 `Method B`라는 두 가지 검색/추천 결과가 제공됩니다. 어느 쪽이 실무 헤드헌팅 관점에서 더 타당하고 설명력 있는 후보자를 끌어왔는지 정밀도(Precision)를 평가해 주세요.\n\n")
        f.write("---\n")
        
        for jd in jds:
            f.write(f"\n## {jd['id']}: {jd['title']}\n")
            f.write(f"- **입력 문장(Gravity Query):** `{jd['query']}`\n")
            f.write(f"- **입력 키워드(Legacy Query Search):** `{', '.join(jd['keywords'])}`\n\n")
            
            # Control (Keyword)
            control_results = rank_keyword_control(jd['keywords'], candidates)
            
            # Test (Gravity)
            # Test (Gravity + Geometry v3)
            mapped_jd_nodes = snapper.extract_and_map_skills(jd['query']) 
            opts = {
                "jd_domain": jd.get("domain"), 
                "core_intents": jd.get("core_intents"),
                "jd_tendency": jd.get("tendency")
            }
            gravity_results = snapper.rank_candidates_for_jd(jd['query'], candidates, opts)
            
            # 무결성을 위해 Method A와 Method B의 순서를 섞을 수 있지만 여기선 가독성을 위해 고정
            # B가 Gravity 로 고정하여 출력하지만 블라인드를 원한다면 변동 가능
            f.write("### 🟥 Method A (Control: Legacy Keyword Multi-Match)\n")
            if not control_results:
                f.write("❌ 조건에 맞는 인재 검색 실패 (0건 발견)\n")
            else:
                for i, r in enumerate(control_results[:5], 1):
                    f.write(f"{i}. **{r['name']}** (Match Score: {r['score']})\n")
                    f.write(f"   - **매칭 키워드:** {', '.join(r['matched_nodes'])}\n")
                    f.write(f"   - **전체 스킬:** {', '.join(r['raw_skills'][:10])}...\n\n")
                    
            f.write("### 🟦 Method B (Test: Gravity Ontology Physics)\n")
            if not gravity_results:
                f.write("❌ 궤도 내에서 인력을 받는 인재 검색 실패 (0건 발견)\n")
            else:
                for i, r in enumerate(gravity_results[:5], 1):
                    matched_list = []
                    for k, v in r['matched_nodes'].items():
                        matched_list.append(f"{k}(wt:{v:.1f})")
                    
                    f.write(f"{i}. **{r['name']}** (Gravity Score: {r['score']:.2f})\n")
                    f.write(f"   - **견인 항성(Vector Space):** {', '.join(matched_list)}\n")
                    f.write(f"   - **전체 스킬:** {', '.join(r['raw_skills'][:10])}...\n\n")
                    
            f.write("---\n")
            
    print(f"✅ Generated A/B Evaluation Report successfully at {output_path}")

if __name__ == "__main__":
    run_ab_test()
