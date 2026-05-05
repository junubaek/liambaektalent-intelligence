import sqlite3
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI
from neo4j import GraphDatabase
from connectors.pinecone_api import PineconeClient

# ─────────────────────────────────────────
# 0. 사전 데이터 보정 (김광우, 김완희)
# ─────────────────────────────────────────
conn = sqlite3.connect("candidates.db", timeout=20)
cur = conn.cursor()

print("=== 사전 데이터 보정 ===")
# 김광우
cur.execute("UPDATE candidates SET current_company = 'HyundaiCard', is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE name_kr LIKE '%김광우%' AND is_duplicate = 0")
# 김완희
cur.execute("UPDATE candidates SET current_company = 'KB 부동산신탁', is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE name_kr LIKE '%김완희%' AND is_duplicate = 0")
conn.commit()
print("김광우/김완희 소속 회사 반영 완료.\n")

# ─────────────────────────────────────────
# 1. 설정 및 클라이언트 준비
# ─────────────────────────────────────────
with open("secrets.json", "r") as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"):
    pc_host = f"https://{pc_host}"
pc = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)

# [중요] 원격 Neo4j 사용
n_uri = secrets.get("NEO4J_URI", "bolt://localhost:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

HIDDEN_MAP = {
    "상장": ["IPO", "IPO_Preparation"],
    "기업공개": ["IPO", "IPO_Preparation"],
    "투자자": ["Investor_Relations", "IR"],
    "기업설명회": ["Investor_Relations", "IR"],
    "반도체 설계": ["RTL_Design", "Circuit_Design"],
    "시스템반도체": ["System_on_Chip", "SoC"],
    "테스트 설계": ["Design_for_Testability", "DFT"],
    "재무모델": ["Financial_Modeling"],
    "재무모델링": ["Financial_Modeling"],
    "데이터시각화": ["Tableau", "Data_Visualization"],
    "시각화": ["Tableau", "Data_Visualization"],
    "클라우드 서비스": ["SaaS", "Cloud_Computing"],
    "물류 자동화": ["ASRS", "Warehouse_Automation"],
    "자동창고": ["ASRS", "Warehouse_Automation"],
    "ERP 시스템": ["SAP_ERP", "ERP"],
    "영업 자동화": ["DevOps", "CI_CD"],
    "앱 개발": ["Kotlin", "Android_Development"],
    "안드로이드": ["Kotlin", "Android_Development"],
    "프로덕트": ["Product_Management", "Product_Owner"],
    "제품 기획": ["Product_Management", "Product_Owner"],
    "PO": ["Product_Owner", "Product_Management"],
    "PM": ["Product_Management", "Project_Management"],
    "서비스 기획": ["Product_Management", "Service_Planning"],
    "UX": ["UX_Design", "User_Experience"],
    "유저 리서치": ["User_Research", "UX_Design"],
    "로드맵": ["Product_Roadmap", "Product_Management"],
    "스프린트": ["Agile", "Scrum"],
    "애자일": ["Agile", "Scrum"],
}

def inject_hidden_keywords(text: str) -> str:
    found = set()
    for ko_word, en_tags in HIDDEN_MAP.items():
        if ko_word in text:
            found.update(en_tags)
    if found:
        return text + f"\n[Keywords: {', '.join(list(found))}]"
    return text

def chunk_text(text: str, chunk_size: int = 1000):
    if not text:
        return []
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return [inject_hidden_keywords(c) for c in chunks]

# 타겟: is_neo4j_synced=0 OR is_pinecone_synced=0 인 마스터
cur.execute("""
    SELECT id, name_kr, raw_text, profile_summary, current_company, sector
    FROM candidates
    WHERE is_duplicate = 0
      AND (is_neo4j_synced = 0 OR is_pinecone_synced = 0)
""")
targets = cur.fetchall()

print(f"재색인 타겟: {len(targets)}명")
print()

success = 0
fail = 0
session = driver.session()

for i, row in enumerate(targets):
    cid, name, raw_text, summary, current_company, sector = row

    if not raw_text and not summary:
        print(f"  [{i+1}] ⚠️  {name} — raw_text/summary 없음, 스킵")
        continue

    try:
        # 1. Neo4j 업데이트
        session.run("""
            MATCH (n:Candidate {id: $cid})
            SET n.summary = $summary,
                n.current_company = $company,
                n.sector = $sector
        """, cid=str(cid), summary=summary or "", company=current_company or "", sector=sector or "미분류")

        # 2. Pinecone 기존 벡터 삭제
        try:
            pc.delete(filter_meta={"candidate_id": str(cid)}, namespace="resume_vectors")
        except:
            pass

        # 3. 재임베딩
        embed_text = raw_text if raw_text else summary
        chunks = chunk_text(embed_text)
        if chunks:
            emb_res = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=chunks
            )
            vectors = [{
                "id": f"{cid}_chunk_{idx}",
                "values": ed.embedding,
                "metadata": {"candidate_id": str(cid), "chunk_index": idx}
            } for idx, ed in enumerate(emb_res.data)]
            pc.upsert(vectors, namespace="resume_vectors")

        # 4. DB 동기화 상태 업데이트
        cur.execute("""
            UPDATE candidates SET is_neo4j_synced = 1, is_pinecone_synced = 1
            WHERE id = ?
        """, (cid,))
        conn.commit()

        success += 1
        print(f"  [{i+1}/{len(targets)}] ✓ {name} | {current_company}")

    except Exception as e:
        fail += 1
        print(f"  [{i+1}/{len(targets)}] ✗ {name} — 오류: {e}")

    time.sleep(0.05)

session.close()
driver.close()
conn.close()

print(f"\n=== 완료 ===")
print(f"성공: {success}명 / 실패: {fail}명")
