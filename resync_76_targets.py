import sqlite3
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI
from neo4j import GraphDatabase
from connectors.pinecone_api import PineconeClient

# ─────────────────────────────────────────
# 설정
# ─────────────────────────────────────────
with open("secrets.json", "r") as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))

pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"):
    pc_host = f"https://{pc_host}"
pc = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))
conn = sqlite3.connect("candidates.db", timeout=20)
cur = conn.cursor()

# ─────────────────────────────────────────
# Hidden Keyword 주입 (batch_pinecone_sync.py 동일 로직)
# ─────────────────────────────────────────
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
    "안드로이드": ["Kotlin", "Android_Development"]
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

# ─────────────────────────────────────────
# 타겟 로드
# ─────────────────────────────────────────
with open("resync_targets.json", "r", encoding="utf-8") as f:
    target_ids = json.load(f)

print(f"재색인 타겟: {len(target_ids)}명")
print()

# ─────────────────────────────────────────
# 메인 재색인 루프
# ─────────────────────────────────────────
success = 0
fail = 0
skip = 0

session = driver.session()

for i, cid in enumerate(target_ids):
    cur.execute("""
        SELECT id, name_kr, raw_text, profile_summary, current_company, sector
        FROM candidates
        WHERE id = ? AND is_duplicate = 0
    """, (cid,))
    row = cur.fetchone()

    if not row:
        print(f"  [{i+1}] ⚠️  ID {cid[:8]}... — DB에 없거나 is_duplicate=1, 스킵")
        skip += 1
        continue

    cid, name, raw_text, summary, current_company, sector = row

    if not raw_text and not summary:
        print(f"  [{i+1}] ⚠️  {name} — raw_text/summary 둘 다 없음, 스킵")
        skip += 1
        continue

    try:
        # 1. Neo4j 속성 업데이트
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

        # 3. Pinecone 재임베딩 & upsert
        embed_text = raw_text if raw_text else summary
        chunks = chunk_text(embed_text)

        if chunks:
            emb_res = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=chunks
            )
            vectors = []
            for idx, ed in enumerate(emb_res.data):
                vectors.append({
                    "id": f"{cid}_chunk_{idx}",
                    "values": ed.embedding,
                    "metadata": {
                        "candidate_id": str(cid),
                        "chunk_index": idx
                    }
                })
            pc.upsert(vectors, namespace="resume_vectors")

        # 4. DB 동기화 상태 업데이트
        cur.execute("""
            UPDATE candidates
            SET is_pinecone_synced = 1, is_neo4j_synced = 1
            WHERE id = ?
        """, (cid,))

        success += 1
        print(f"  [{i+1}/{len(target_ids)}] ✓ {name} | {current_company}")

    except Exception as e:
        fail += 1
        print(f"  [{i+1}/{len(target_ids)}] ✗ {name} — 오류: {e}")

    # 50명마다 커밋 + 진행상황
    if (i + 1) % 50 == 0:
        conn.commit()
        print(f"\n  중간 저장 완료 ({i+1}/{len(target_ids)})\n")

    time.sleep(0.05)  # rate limit 방지

conn.commit()
session.close()
driver.close()
conn.close()

print()
print(f"=== 재색인 완료 ===")
print(f"성공: {success}명")
print(f"실패: {fail}명")
print(f"스킵: {skip}명")
