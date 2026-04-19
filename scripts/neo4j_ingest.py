import os
import json
from neo4j import GraphDatabase
import logging
from app.graph_engine.core_graph import SkillGraphEngine
from app.graph_engine.obsidian_parser import ObsidianParser
from app.engine.resume_snap import CandidateSnapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Neo4jIngest")

class Neo4jIngestionPipeline:
    def __init__(self, uri, user, password, vault_path, candidates_file):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        self.graph_engine = SkillGraphEngine(use_v7=True)
        
        self.snapper = CandidateSnapper(self.graph_engine)
        self.candidates_file = candidates_file
        
    def close(self):
        self.driver.close()

    def load_candidates(self):
        if not os.path.exists(self.candidates_file):
            logger.error(f"Candidates file not found: {self.candidates_file}")
            return []
        with open(self.candidates_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        results = data.get('results', [])
        candidates_list = []
        for i, c in enumerate(results):
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

            candidates_list.append({
                "id": c.get("id", f"C_{i}"),
                "name": name,
                "raw_skills": list(set(skills)),
                "sectors": {"Main Sector": ",".join(main_sectors)}
            })
        return candidates_list

    def ingest_ontology(self):
        """1단계: Obsidian Vault의 그래프 모델을 Neo4j로 복제"""
        logger.info("Starting Ontology (Skills) Ingestion...")
        skills = list(self.graph_engine.graph.nodes())
        
        with self.driver.session() as session:
            # 1. 모든 Skill Node 생성
            for skill in skills:
                # Category 구하기
                cat = "General"
                categories = {
                    "Sales": ["영업", "sales", "b2b", "해외", "md", "마케팅", "퍼포먼스", "그로스", "브랜드", "crm", "콘텐츠", "홍보", "pr"],
                    "Tech": ["tech", "software", "소프트웨어", "sw", "인프라", "cloud", "devops", "sre", "be", "fe", "mobile", "ios", "android", "data", "데이터", "ai", "machinelearning", "mlops", "엔지니어", "모델링", "dba", "반도체", "hw", "하드웨어", "설계", "연구", "r&d", "임베디드", "펌웨어", "fw", "공정", "plc", "자동화"],
                    "Product": ["product", "기획(화면설계", "uiux", "ui", "ux", "po", "pm", "서비스", "제품"],
                    "Business": ["전략", "경영", "strategy", "hr", "재무", "finance", "회계", "m&a", "투자", "물류", "scm", "유통", "컴플라이언스", "법무", "operation", "사업", "운영"]
                }
                name_low = skill.lower()
                for c_name, c_list in categories.items():
                    if any(kw in name_low for kw in c_list):
                        cat = c_name
                        break
                
                query = """
                MERGE (s:Skill {name: $name})
                SET s.category = $category
                """
                session.run(query, name=skill, category=cat)
            
            # 2. Edge (DEPENDS_ON / SIMILAR_TO) 생성
            for skill in skills:
                adj = self.graph_engine.get_adjacent_skills(skill, max_distance=1)
                for dst, info in adj.items():
                    if dst != skill: # 자기 자신 제외
                        query = """
                        MATCH (s1:Skill {name: $src}), (s2:Skill {name: $dst})
                        MERGE (s1)-[r:SIMILAR_TO]->(s2)
                        SET r.distance = $dist
                        """
                        session.run(query, src=skill, dst=dst, dist=info.get("distance", 1.0))
        
        logger.info(f"Ontology Ingestion Complete: {len(skills)} nodes.")

    def ingest_candidates(self):
        """2단계: Candidate JSON을 Neo4j로 전송하고 HAS_SKILL 관계 생성"""
        logger.info("Starting Candidate Ingestion...")
        candidates = self.load_candidates()
        
        # DF(Document Frequency) 계산 준비
        df_map = {}
        for cand in candidates:
            cand_skills_raw = cand.get("raw_skills", [])
            cand_nodes = self.snapper.extract_and_map_skills(cand_skills_raw)
            for k in cand_nodes:
                df_map[k] = df_map.get(k, 0) + 1
                
        # 스킬 DF, Mass 업데이트
        N = len(candidates)
        with self.driver.session() as session:
            for skill, df in df_map.items():
                deg = self.graph_engine.get_node_degree(skill)
                mass = self.snapper.calculate_node_mass(deg, df, N)
                
                query = """
                MATCH (s:Skill {name: $name})
                SET s.df = $df, s.mass = $mass, s.degree = $deg
                """
                session.run(query, name=skill, df=df, mass=mass, deg=deg)
        
        # Candidate 생성 및 연결
        with self.driver.session() as session:
            total = len(candidates)
            for i, cand in enumerate(candidates):
                cand_name = cand.get("name", "Unknown")
                cand_id = cand.get("id", f"C_{i}")
                main_sectors = cand.get("sectors", {}).get("Main Sector", "")
                
                cand_skills_raw = cand.get("raw_skills", [])
                cand_nodes = self.snapper.extract_and_map_skills(cand_skills_raw)
                cand_tendency = self.snapper.get_tendency_vector(cand_nodes)
                
                # 후보자 노드 생성
                query_create_cand = """
                MERGE (c:Candidate {id: $cid})
                SET c.name = $name, c.sectors = $sectors,
                    c.tendency_sales = $ts, c.tendency_tech = $tt,
                    c.tendency_product = $tp, c.tendency_biz = $tb
                """
                session.run(query_create_cand, cid=cand_id, name=cand_name, sectors=main_sectors,
                            ts=cand_tendency["Sales"], tt=cand_tendency["Tech"],
                            tp=cand_tendency["Product"], tb=cand_tendency["Business"])
                
                # 후보자-스킬 매핑 생성
                for skill, weight in cand_nodes.items():
                    query_rel = """
                    MATCH (c:Candidate {id: $cid}), (s:Skill {name: $sname})
                    MERGE (c)-[r:HAS_SKILL]->(s)
                    SET r.raw_weight = $weight
                    """
                    session.run(query_rel, cid=cand_id, sname=skill, weight=weight)
                    
                if (i+1) % 50 == 0:
                    logger.info(f"Processed {i+1}/{total} candidates.")
                    
        logger.info("Candidate Ingestion Complete.")

    def run_all(self):
        # Neo4j 데이터 초기화 (전체 삭제 후 재구축)
        logger.info("Purging existing Neo4j Database for V7.1 Clean Ingestion...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
        self.ingest_ontology()
        self.ingest_candidates()
        self.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest Notion DB and Obsidian Vault into Neo4j")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="toss1234")
    
    args = parser.parse_args()
    
    VAULT_DIR = "c:/Users/cazam/Downloads/이력서자동분석검색시스템/obsidian_vault"
    CANDIDATES_JSON = "c:/Users/cazam/Downloads/이력서자동분석검색시스템/temp_500_candidates.json"
    
    pipeline = Neo4jIngestionPipeline(args.uri, args.user, args.password, VAULT_DIR, CANDIDATES_JSON)
    pipeline.run_all()
    print("🚀 Script finished data ingestion to Neo4j AuraDB.")

