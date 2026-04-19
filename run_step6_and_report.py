import os
import subprocess
import time
from neo4j import GraphDatabase

print("Starting Step 6 parsing in background...", flush=True)
subprocess.run(["python", "dynamic_parser_step6.py"])

print("Parsing complete. Generating report...", flush=True)
report_lines = []
report_lines.append("=== STEP 6 FINAL REPORT ===")

try:
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as s:
        cand_count = s.run("MATCH (c:Candidate) RETURN count(c) as cnt").single()["cnt"]
        edge_count = s.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as cnt").single()["cnt"]
        avg_edges = edge_count / cand_count if cand_count else 0
        
        report_lines.append(f"총 후보자 수: {cand_count} 명")
        report_lines.append(f"총 파싱 완료 엣지 수: {edge_count} 개")
        report_lines.append(f"평균 엣지 수: {avg_edges:.2f} 개 (기존 8.28개 대비 비교용)")
        report_lines.append("에러 케이스: processed_step6.json 로그 참조")
except Exception as e:
    report_lines.append(f"Neo4j 통계 추출 실패: {e}")

print("Running NDCG Evaluation...", flush=True)
try:
    # run NDCG test
    result = subprocess.run(["python", "run_real_evaluate_v3.py"], capture_output=True, encoding='utf-8', errors='ignore')
    report_lines.append("\n=== NDCG@10 측정 결과 ===")
    report_lines.append(result.stdout)
    if result.stderr:
        report_lines.append("\n오류 로그:")
        report_lines.append(result.stderr)
except Exception as e:
    report_lines.append(f"평가 스크립트 실행 실패: {e}")

with open("step6_final_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("All tasks completed successfully. Report saved to step6_final_report.txt.", flush=True)
