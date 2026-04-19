import sqlite3
import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

rules = {
    "BI_Analysis": ["Tableau", "BI", "대시보드", "Power BI", "Looker", "데이터 시각화", "경영 지표"],
    "App_Marketing": ["UA", "앱 마케팅", "앱마케팅", "MAU", "리텐션", "앱스플라이어", "MMP"],
    "QA_Engineering": ["QA", "품질보증", "테스트 자동화", "Selenium", "버그 리포트", "테스트케이스"],
    "Motion_Graphics": ["모션그래픽", "애프터이펙트", "After Effects", "모션 디자인", "영상 편집"],
    "Information_Security": ["정보보안", "보안관제", "ISMS", "취약점 분석", "보안 정책"],
    "Partnership_Management": ["파트너십", "제휴", "파트너 관리", "제휴 마케팅", "파트너 영업"],
    "E_Commerce_Operations": ["이커머스", "e-commerce", "온라인 쇼핑몰", "셀러 관리", "플랫폼 운영"],
    "Commerce_MD": ["MD", "머천다이징", "상품기획", "바이어", "소싱", "카테고리 관리"],
    "Venture_Capital": ["VC", "심사역", "벤처투자", "투자 심사", "Deal Sourcing", "포트폴리오"],
    "Healthcare_PM": ["헬스케어", "의료", "디지털헬스", "EMR", "병원 서비스", "메디컬"],
    "Learning_and_Development": ["L&D", "HRD", "교육 담당", "사내교육", "직무교육", "리더십 교육"],
    "Penetration_Testing": ["모의해킹", "침투테스트", "Penetration", "버그바운티", "취약점 진단"]
}

def build_candidates_map():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT document_hash, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    
    matches = {skill: [] for skill in rules.keys()}
    for doc_hash, text in rows:
        text_lower = text.lower()
        for skill, kws in rules.items():
            if any(kw.lower() in text_lower for kw in kws):
                matches[skill].append(doc_hash)
    return matches

def run_repair():
    print("=== Deep Repair Batch 2 (Advanced 12 Domains) ===")
    matches = build_candidates_map()
    
    with driver.session() as session:
        for skill, doc_hashes in matches.items():
            print(f"Processing {skill} ({len(doc_hashes)} candidates)...")
            count = 0
            for dh in doc_hashes:
                # Add MANAGED edge if it doesn't already exist
                res = session.run("""
                    MATCH (c:Candidate {id: $dh})
                    MERGE (s:Skill {name: $skill})
                    MERGE (c)-[r:MANAGED]->(s)
                    RETURN id(r)
                """, dh=dh, skill=skill)
                if res.single(): count += 1
            print(f" -> Inserted {count} edges for {skill}")

        print("\n=== Edge Counts per Node ===")
        for skill in rules.keys():
            res = session.run("MATCH ()-[r]->(s:Skill {name: $skill}) RETURN count(r) as cnt", skill=skill)
            cnt = res.single()['cnt']
            print(f" - {skill}: {cnt} 엣지")

if __name__ == "__main__":
    run_repair()
