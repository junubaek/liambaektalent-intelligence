import sqlite3
import subprocess

def main():
    # 1. Update SQLite Profile Summary for 안유리 to enrich with Technical Program Manager keywords
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    enrich_summary = (
        "카카오페이 Technical Program Manager (TPM) 및 애자일 코치 (Agile Coach). "
        "컴퓨터비전 공학석사 출신으로 FinTech, Deep Learning 등 기술 중심 도메인에서 대규모 기술 프로젝트 및 프로그램 매니지먼트(Technical Program Management)를 리딩. "
        "Agile 방법론 도입, 조직 개발, 클라우드 인프라 운영까지 폭넓은 경험을 보유한 전문 테크니컬 프로그래밍 매니저."
    )
    
    cur.execute("""
        UPDATE candidates 
        SET profile_summary = ? 
        WHERE id = '79d1edd5-7001-4f71-bc2b-95de15b11101'
    """, (enrich_summary,))
    print(f"SQLite: Updated 안유리 profile_summary. Rows affected: {cur.rowcount}")
    conn.commit()
    conn.close()

    # 2. Run embedding generator to refresh Yura's embedding in Neo4j
    print("\n=== Re-generating Embeddings ===")
    subprocess.run(["python", "scratch_embed_two.py"], check=True)

    # 3. Rebuild BM25 Index
    print("\n=== Re-building BM25 Index ===")
    subprocess.run(["python", "build_bm25_index.py"], check=True)

    print("\nEnrichment and indexing completed successfully.")

if __name__ == "__main__":
    main()
