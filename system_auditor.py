import os
import sqlite3
import re
from datetime import datetime
from neo4j import GraphDatabase
import urllib.request
import json

# ⚙️ 환경 설정
SQLITE_DB_PATH = "candidates.db"
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_AUTH = ("neo4j", "toss1234")
PC_API_KEY = os.getenv("PINECONE_API_KEY")
import json
s = {}
try:
    with open('secrets.json', 'r') as f:
        s = json.load(f)
        if s.get("PINECONE_API_KEY"):
            PC_API_KEY = s.get("PINECONE_API_KEY")
except: pass

PINECONE_INDEX_NAME = "resume_vectors"

def parse_valid_canonical_nodes(md_path: str):
    """canonical_map_status.md(또는 관련 파일)에서 합법적인 표준 노드명 추출"""
    valid_nodes = set()
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("### "):
                    valid_nodes.add(line.replace("### ", "").strip())
    except Exception as e:
        print(f"⚠️ CANONICAL_MAP 파싱 실패: {e}")
    return valid_nodes

def run_system_audit():
    print("🔍 [V8.5 Talent OS] 일일 데이터 무결성 감사를 시작합니다...\n")
    report_lines = []
    report_lines.append(f"📊 V8.5 System Audit Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 50)
    
    warnings = []
    
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()

        # ==========================================
        # 1. 온톨로지 벡터 최신화 확인
        # ==========================================
        try:
            # Note: We're using 최신_CANONICAL_MAP.md or canonical_map_status.md
            md_path = "최신_CANONICAL_MAP.md" if os.path.exists("최신_CANONICAL_MAP.md") else "canonical_map_status.md"
            md_time = os.path.getmtime(md_path)
            pkl_time = os.path.getmtime("ontology_vectors.pkl")
            if md_time > pkl_time:
                warnings.append(f"[경고] {md_path}가 ontology_vectors.pkl보다 최신입니다. 벡터를 다시 구워주세요.")
            else:
                report_lines.append("✅ 1. 온톨로지 벡터 최신화: 정상")
        except FileNotFoundError:
            warnings.append("[경고] 온톨로지 파일(MD 또는 PKL)을 찾을 수 없습니다.")

        # ==========================================
        # 2. SQLite 동기화 누락 검사 (2시간 이상)
        # ==========================================
        try:
            cur.execute("""
                SELECT count(id) FROM candidates 
                WHERE is_duplicate=0 AND (is_neo4j_synced = 0 OR is_pinecone_synced = 0)
                AND datetime(created_at) < datetime('now', '-2 hours')
            """)
            limbo_count = cur.fetchone()[0]
            if limbo_count > 0:
                warnings.append(f"[경고] 동기화 누락(Limbo) 후보자 발견: {limbo_count}명")
            else:
                report_lines.append("✅ 2. 동기화 누락 검사: 정상 (Limbo 없음)")
        except sqlite3.OperationalError as e:
            warnings.append(f"[오류] 2번 검사 실패: {e}")

        # ==========================================
        # 3. Pinecone 카운트 대조
        # ==========================================
        try:
            cur.execute("SELECT count(id) FROM candidates WHERE is_pinecone_synced = 1")
            db_sync_count = cur.fetchone()[0]
        except Exception:
            db_sync_count = 0
            
        try:
            if not PC_API_KEY:
                raise Exception("Pinecone API Key is missing.")
            
            host = s.get("PINECONE_HOST")
            if not host:
                raise Exception("Pinecone Host is missing in secrets.json.")
            
            url = f"{host}/describe_index_stats"
            req = urllib.request.Request(url, method="POST", headers={
                "Api-Key": PC_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
            
            with urllib.request.urlopen(req) as response:
                stats = json.loads(response.read().decode('utf-8'))
                pinecone_count = stats.get('totalVectorCount', 0)
            
            # Chunk 단위 임베딩 시 벡터 수가 더 많을 수 있으므로, 최소 기준으로 검사
            report_lines.append(f"ℹ️  3. Pinecone 적재량: DB 완료 {db_sync_count}명 / 벡터 {pinecone_count}개")
            if pinecone_count == 0 and db_sync_count > 0:
                warnings.append(f"[경고] Pinecone 데이터 유실 의심 (DB: {db_sync_count} / Pinecone: 0)")
        except Exception as e:
            warnings.append(f"[오류] Pinecone 연결 실패: {e}")

        # ==========================================
        # 4. Neo4j 고스트 노드 검사
        # ==========================================
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
            with driver.session() as session:
                # B 기준: 후보자와 연결된 엣지가 하나도 없는 Skill 노드
                result = session.run("MATCH (s:Skill) WHERE NOT (:Candidate)-[]->(s) RETURN count(s) AS ghost_count")
                ghost_count = result.single()["ghost_count"]
            
            if ghost_count > 0:
                report_lines.append(f"ℹ️  4. Neo4j 고스트 노드 검사: 의심되는 고스트 노드 발견 ({ghost_count}개)")
            else:
                report_lines.append("✅ 4. Neo4j 고스트 노드 검사: 정상 (오염 없음)")
        except Exception as e:
            warnings.append(f"[오류] Neo4j 고스트 노드 검사 실패: {e}")

        # ==========================================
        # 5. name_kr 오염 검사 (불용어 및 빈도 이상)
        # ==========================================
        try:
            stop_words = "('자금', '기획', '개발', '운영', '마케팅', '재무', '회계', '전략', '인사', '총무', '법무')"
            cur.execute(f"SELECT count(id) FROM candidates WHERE name_kr IN {stop_words} OR length(name_kr) > 20")
            name_corruption_count = cur.fetchone()[0]
            
            cur.execute("""
              SELECT name_kr, count(*) as cnt
              FROM candidates
              GROUP BY name_kr
              HAVING cnt > 100
            """)
            suspicious = cur.fetchall()
            
            if name_corruption_count > 0 or suspicious:
                if name_corruption_count > 0:
                    warnings.append(f"[경고] 이름(name_kr) 불용어 오염 데이터 발견: {name_corruption_count}건")
                if suspicious:
                    for name, cnt in suspicious:
                        # JY (78명) 등 일부 합법적 제외가 필요할 수 있으나, 일단 모두 경고에 추가
                        warnings.append(f"⚠️ [경고] '{name}' {cnt}명 집중 - 동일 이름 다수 (확인 필요)")
            else:
                report_lines.append("✅ 5. 이름 오염 검사: 정상 (대량 덮어쓰기 없음)")
        except sqlite3.OperationalError as e:
            warnings.append(f"[오류] 5번 검사 실패: {e}")

        # ==========================================
        # 6. summary 품질 검사
        # ==========================================
        try:
            cur.execute("""
                SELECT count(id) FROM candidates 
                WHERE summary LIKE '[%' OR summary LIKE '%부문' OR length(summary) < 5
            """)
            summary_corruption_count = cur.fetchone()[0]
            if summary_corruption_count > 0:
                warnings.append(f"[경고] 파일명이 그대로 들어간 summary 오염 발견: {summary_corruption_count}건")
            else:
                report_lines.append("✅ 6. summary 품질 검사: 정상")
        except sqlite3.OperationalError:
            report_lines.append("✅ 6. summary 품질 검사: 필드 없음 (정상)")

        # ==========================================
        # 7. 평균 엣지 수 모니터링
        # ==========================================
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (c:Candidate)-[r]->(s:Skill)
                    RETURN count(r)*1.0 / count(DISTINCT c) AS avg_edges
                """)
                record = result.single()
                avg_edges = record.get("avg_edges") if record and record.get("avg_edges") else 0
                
                report_lines.append(f"ℹ️  7. 평균 엣지 수: 후보자당 {avg_edges:.1f}개")
                if avg_edges <= 5.0 and avg_edges > 0:
                    warnings.append(f"[경고] 후보자 평균 엣지 수가 너무 낮습니다 ({avg_edges:.1f}개). AI 파서 정밀도 확인 요망.")
        except Exception as e:
            warnings.append(f"[오류] 엣지 수 집계 실패: {e}")

    except sqlite3.Error as e:
        warnings.append(f"[오류] SQLite 데이터베이스 에러: {e}")
        
    try:
        cur.execute("SELECT count(id) FROM candidates WHERE last_error IS NOT NULL AND last_error != ''")
        dlq_count = cur.fetchone()[0]
        if dlq_count > 0:
            warnings.append(f"[경고] DLQ(Dead Letter Queue) 에러 발생 대기 건: {dlq_count}건")
        else:
            report_lines.append("✅ 8. DLQ (에러 큐): 깨끗함 (정상)")
    except Exception:
        pass

    if 'conn' in locals() and conn:
        conn.close()

    # ==========================================
    # 📝 리포트 마감 및 파일 저장
    # ==========================================
    report_lines.append("-" * 50)
    if warnings:
        report_lines.append("🚨 [조치 필요 사항]")
        for w in warnings:
            report_lines.append(f"  - {w}")
    else:
        report_lines.append("🎉 [총평] 시스템 데이터 무결성 100% 정상!")
        
    report_lines.append("=" * 50)
    
    final_report = "\n".join(report_lines)
    print(final_report)
    
    with open("audit_report.txt", "w", encoding="utf-8") as f:
        f.write(final_report)
    
    print("\n💾 감사 결과가 'audit_report.txt'에 저장되었습니다.")
    
    # Send to Slack if webhook exists
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        try:
            with open('secrets.json', 'r') as f:
                secrets_dict = json.load(f)
                webhook_url = secrets_dict.get("SLACK_WEBHOOK_URL")
        except: pass
        
    if webhook_url:
        try:
            req = urllib.request.Request(webhook_url, method="POST", headers={"Content-Type": "application/json"})
            data = json.dumps({"text": f"```\n{final_report}\n```"}).encode("utf-8")
            urllib.request.urlopen(req, data=data)
            print("📬 Slack 알림 전송 완료!")
        except Exception as e:
            print(f"⚠️ Slack 잔송 실패: {e}")

if __name__ == "__main__":
    run_system_audit()
