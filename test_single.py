import sys, os, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:/Users/cazam/Downloads/이력서자동분석검색시스템")
sys.path.insert(0, os.getcwd())
from incremental_ingest_v11 import process_file
fp = r"C:/Users/cazam/Downloads/02_resume 전처리/(국문 이력서) Jaein Kim_ver2.0.pdf"
ok, result = process_file(fp)
print("결과:", ok, result)
if ok:
    conn = sqlite3.connect("candidates.db")
    cur = conn.cursor()
    cur.execute("SELECT name_kr, current_company, sector, total_years, has_big_company, has_startup, google_drive_url FROM candidates ORDER BY created_at DESC LIMIT 1")
    r = cur.fetchone()
    print("name_kr:", r[0])
    print("company:", r[1])
    print("sector:", r[2])
    print("total_years:", r[3])
    print("has_big_company:", r[4])
    print("has_startup:", r[5])
    print("drive_url:", str(r[6])[:60] if r[6] else None)
    conn.close()
