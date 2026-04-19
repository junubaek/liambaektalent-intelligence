import os
import json
import sqlite3
from neo4j import GraphDatabase

def get_sqlite_total():
    try:
        db = sqlite3.connect("candidates.db")
        cur = db.cursor()
        cur.execute("SELECT count(*) FROM candidates")
        cnt = cur.fetchone()[0]
        db.close()
        return cnt
    except:
        return 0

def get_total_candidates():
    driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    try:
        with driver.session() as session:
            result = session.run("MATCH (c:Candidate) RETURN count(c) AS count")
            return int(result.single()['count'])
    except Exception as e:
        print(f"Neo4j Query Error: {e}")
        return 0

def get_new_candidates_count():
    try:
        if os.path.exists("preflight_unique.json"):
            with open("preflight_unique.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return len(data)
    except:
        pass
    return 0
    
def get_update_dupes_count():
    # checking update_candidates.json
    try:
        if os.path.exists("update_candidates.json"):
            with open("update_candidates.json", "r", encoding="utf-8") as f:
                return len(json.load(f))
    except:
        pass
        
    try:
        if os.path.exists("preflight_updates.json"):
            with open("preflight_updates.json", "r", encoding="utf-8") as f:
                return len(json.load(f))
    except:
        pass
    return 0

def main():
    print("="*40)
    print("      최종 처리 통계 (Final Stats)     ")
    print("="*40)
    print(f"- 신규 추가된 후보자 수: {get_new_candidates_count()}명")
    print(f"- 총 후보자 수 (Neo4j DB 기준): {get_total_candidates()}명")
    print(f"- 총 후보자 수 (SQLite 기준): {get_sqlite_total()}명")
    print(f"- update_candidates.json에 기록된 중복 건수: {get_update_dupes_count()}건")
    print("="*40)

if __name__ == "__main__":
    main()
