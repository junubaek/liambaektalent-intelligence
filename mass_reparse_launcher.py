import time
import shutil
import datetime
import json
import os
import subprocess
from neo4j import GraphDatabase

def main():
    print("🚀 [1/3] processed.json 백업 시작...")
    today = datetime.datetime.now().strftime("%Y%m%d")
    backup_file = f"processed_backup_{today}.json"
    shutil.copy("processed.json", backup_file)
    print(f"✅ 백업 완료: {backup_file}")
    
    print("🚀 [2/3] processed.json 초기화 (Neo4j 기존 데이터는 유지)")
    with open("processed.json", "w", encoding="utf-8") as f:
        json.dump({}, f)
    print("✅ 초기화 완료. (dynamic_parser.py가 재파싱 시 기존 엣지를 덮어쓰도록 설계됨)")
    
    print("🚀 [3/3] dynamic_parser.py 실행 시작...")
    # Get initial edge count
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        # Before total edges
        res = session.run("MATCH (c:Candidate)-[r]->() RETURN count(r) as ct")
        start_edges = res.single()['ct']
    
    start_time = time.time()
    
    # Run the parser in subprocess
    process = subprocess.Popen(["python", "dynamic_parser.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
    # Save log to file
    with open(f"mass_reparse_log_{today}.txt", "w", encoding="utf-8") as file:
        for line in process.stdout:
            file.write(line)
            file.flush()
    
    process.wait()
    end_time = time.time()
    
    elapsed_hours = (end_time - start_time) / 3600
    
    print("🚀 실행 완료! 분석 진행 중...")
    
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate)-[r]->() RETURN count(r) as ct, count(distinct c) as c_ct")
        row = res.single()
        end_edges = row['ct']
        total_candidates = row['c_ct']
        avg_edges = end_edges / total_candidates if total_candidates > 0 else 0
        
    with open("processed.json", "r", encoding="utf-8") as f:
        try:
            processed = json.load(f)
            parsed_count = len(processed)
        except:
            parsed_count = -1
            
    # Check fallback count from logs easily
    fallback_count = 0
    with open(f"mass_reparse_log_{today}.txt", "r", encoding="utf-8") as file:
        log_content = file.read()
        fallback_count = log_content.count("[Fallback]")
        
    report = f"""
==================================================
🏆 전면 재파싱(Mass Re-parsing) 완료 및 성과 리포트
==================================================
- 소요 시간: {elapsed_hours:.2f} 시간
- 총 파싱 시도 대상: {parsed_count}명
- Fallback (에러/누락 복구 처리) 횟수: {fallback_count}건

- 평균 엣지 수 변화:
   * (기존 목표 평균: 16.4개)
   * 재파싱 후 평균 엣지 수: {avg_edges:.1f}개 (총 엣지 {end_edges}개 / {total_candidates}명의 후보자)
==================================================
"""
    with open("mass_reparse_report_final.txt", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(report)
    driver.close()

if __name__ == "__main__":
    main()
