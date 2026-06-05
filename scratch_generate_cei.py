import json, sqlite3, time
from cei_generator import generate_cei
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 1. Fetch target records
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Get the general batch candidates (all candidates where is_duplicate = 0 AND cei_json IS NULL)
cur.execute("""
    SELECT id, name_kr, current_company,
           sector, raw_text, careers_json, profile_summary
    FROM candidates
    WHERE is_duplicate = 0
    AND cei_json IS NULL
    ORDER BY
        CASE
            WHEN raw_text IS NOT NULL
             AND length(raw_text) > 300 THEN 0
            WHEN profile_summary IS NOT NULL
             AND length(profile_summary) > 50 THEN 1
            ELSE 2
        END
""")
rows = cur.fetchall()
cols = ['id','name_kr','current_company',
        'sector','raw_text','careers_json','profile_summary']
candidates = [dict(zip(cols, r)) for r in rows]
conn.close()

print(f'처리 대상: {len(candidates)}명')

# node_idf 로드
node_idf = json.load(open('node_idf.json', encoding='utf-8'))

def process_candidate(cand):
    # Process single candidate using a dedicated connection for reading
    db_conn = sqlite3.connect('candidates.db', timeout=60.0)
    try:
        cei = generate_cei(cand, db_conn, node_idf)
        return True, (cand['id'], cei, cand.get("name_kr") or "Unknown")
    except Exception as e:
        name = cand.get("name_kr") or "Unknown"
        return False, (name, str(e))
    finally:
        db_conn.close()

success, failed = 0, 0
pending_updates = []

def save_batch(batch):
    if not batch:
        return
    db_conn = sqlite3.connect('candidates.db', timeout=60.0)
    db_cur = db_conn.cursor()
    try:
        for cid, cei, name in batch:
            db_cur.execute("""
                UPDATE candidates
                SET cei_json = ?,
                    cei_confidence = ?,
                    cei_updated_at = ?
                WHERE id = ?
            """, (
                json.dumps(cei, ensure_ascii=False),
                cei['confidence'],
                datetime.now().isoformat(),
                cid
            ))
        db_conn.commit()
    except Exception as e:
        print(f"일괄 저장 중 오류 발생: {e}")
        # fallback to individual save to be safe
        db_conn.rollback()
        for cid, cei, name in batch:
            try:
                db_cur.execute("""
                    UPDATE candidates
                    SET cei_json = ?,
                        cei_confidence = ?,
                        cei_updated_at = ?
                    WHERE id = ?
                """, (
                    json.dumps(cei, ensure_ascii=False),
                    cei['confidence'],
                    datetime.now().isoformat(),
                    cid
                ))
                db_conn.commit()
            except Exception as ex:
                print(f"개별 저장 실패 (ID: {cid}): {ex}")
                db_conn.rollback()
    finally:
        db_conn.close()

# Use 20 threads for concurrent calling
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(process_candidate, c) for c in candidates]
    for idx, fut in enumerate(futures):
        try:
            ok, res = fut.result()
            if ok:
                success += 1
                pending_updates.append(res)
            else:
                failed += 1
                print(f"오류: {res[0]} - {res[1]}")
        except Exception as e:
            failed += 1
            print(f"퓨처 에러: {e}")

        # 500명마다 중간 저장
        if len(pending_updates) >= 500 or (idx + 1) == len(candidates):
            save_batch(pending_updates)
            print(f'--- 중간 저장 완료 ({len(pending_updates)}명) ---')
            pending_updates.clear()

        if (idx + 1) % 50 == 0 or idx + 1 == len(candidates):
            print(f'진행률: {idx + 1}/{len(candidates)} 완료 | 성공: {success}명, 실패: {failed}명')
            
        time.sleep(0.01)

print(f'최종: 성공 {success}명, 실패 {failed}명')
