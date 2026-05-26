import shutil
import datetime
import sqlite3
import sys
import os

# Set stdout to UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
db_path = os.path.join(PROJECT_ROOT, "candidates.db")

def main():
    # 1. Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    backup_path = os.path.join(PROJECT_ROOT, f"candidates_backup_{timestamp}.db")
    print(f"1. [백업 시작] {db_path} -> {backup_path}")
    try:
        shutil.copy(db_path, backup_path)
        print(f"   ✅ 백업 완료: {os.path.basename(backup_path)}")
    except Exception as e:
        print(f"   ❌ 백업 실패: {e}")
        return

    # 2. Merge
    print("\n2. [병합 시작] 139명 동일인물 병합 및 서브 레코드 정리...")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute('''SELECT id, name_kr, email, phone, birth_year, total_years,
                       length(coalesce(raw_text,'')) as tlen
                       FROM candidates WHERE is_duplicate=0''')
        candidates = cur.fetchall()

        # DSU
        parent = {c[0]: c[0] for c in candidates}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        def clean_email(e):
            if not e: return None
            e = e.strip().lower()
            if any(p in e for p in ['saramin','jobkorea','incruit','wanted']): return None
            return e

        def clean_phone(p):
            if not p: return None
            return p.replace('-','').replace(' ','').strip()

        email_map, phone_map = {}, {}
        for c in candidates:
            cid, name, email, phone = c[0], c[1], c[2], c[3]
            ce = clean_email(email)
            cp = clean_phone(phone)
            if ce:
                key = (name, ce)
                if key in email_map: union(cid, email_map[key][0])
                email_map.setdefault(key, []).append(cid)
            if cp:
                key = (name, cp)
                if key in phone_map: union(cid, phone_map[key][0])
                phone_map.setdefault(key, []).append(cid)

        # 그룹화
        groups = {}
        for c in candidates:
            root = find(c[0])
            groups.setdefault(root, []).append(c)

        dup_groups = {r: m for r, m in groups.items() if len(m) > 1}
        print(f"   - 식별된 병합 대상 그룹: {len(dup_groups)}개")

        merged = 0
        for root, members in dup_groups.items():
            # 마스터: raw_text 가장 긴 것
            master = max(members, key=lambda x: x[6])
            master_id = master[0]
            
            # 마스터에 없는 필드 서브에서 보완
            fill_phone = master[3]
            fill_email = master[2]
            fill_birth = master[4]
            fill_years = master[5]
            
            for sub in members:
                if sub[0] == master_id: continue
                if not fill_phone and sub[3]: fill_phone = sub[3]
                if not fill_email and clean_email(sub[2]): fill_email = sub[2]
                if not fill_birth and sub[4]: fill_birth = sub[4]
                if not fill_years and sub[5]: fill_years = sub[5]
            
            # 마스터 업데이트
            cur.execute('''UPDATE candidates SET
                phone=coalesce(phone,?), email=coalesce(email,?),
                birth_year=coalesce(birth_year,?), total_years=coalesce(total_years,?),
                is_neo4j_synced=0, is_pinecone_synced=0
                WHERE id=?''',
                (fill_phone, fill_email, fill_birth, fill_years, master_id))
            
            # 서브 중복 처리 (duplicate_of 에 마스터 ID도 같이 매핑)
            for sub in members:
                if sub[0] == master_id: continue
                cur.execute('''UPDATE candidates SET 
                    is_duplicate=1, 
                    duplicate_of=?, 
                    is_neo4j_synced=0, 
                    is_pinecone_synced=0 
                    WHERE id=?''', (master_id, sub[0]))
                merged += 1

        conn.commit()
        conn.close()
        print(f"   ✅ 병합 성공: {merged}개 서브 레코드 중복 처리 완료")
    except Exception as e:
        print(f"   ❌ 병합 실패: {e}")

if __name__ == "__main__":
    main()
