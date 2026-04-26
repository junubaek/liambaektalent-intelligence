import sqlite3
import pandas as pd
from neo4j import GraphDatabase

EXCEL_FILE = 'candidate_ui_data_export.csv.xlsx'
DB_PATH = 'candidates.db'

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get existing DB state
cur.execute("SELECT id, name_kr, phone, email, current_company FROM candidates")
db_rows = {row['id']: dict(row) for row in cur.fetchall()}

# Load Excel
df = pd.read_excel(EXCEL_FILE)
df = df.fillna('')

update_queue = []

for _, row in df.iterrows():
    c_id = str(row['ID']).strip()
    if c_id not in db_rows:
        continue
        
    db_c = db_rows[c_id]
    
    excel_name = str(row['Name_KR']).strip()
    excel_phone = str(row['Phone']).strip()
    excel_email = str(row['Email']).strip()
    excel_company = str(row['Current_Company']).strip()
    
    db_name = str(db_c['name_kr'] or '').strip()
    db_phone = str(db_c['phone'] or '').strip()
    db_email = str(db_c['email'] or '').strip()
    db_company = str(db_c['current_company'] or '').strip()
    
    if excel_name != db_name or excel_phone != db_phone or excel_email != db_email or excel_company != db_company:
        update_queue.append({
            'id': c_id,
            'name_kr': excel_name,
            'phone': excel_phone,
            'email': excel_email,
            'current_company': excel_company
        })

print(f"Found {len(update_queue)} records to update!")

if update_queue:
    # 1. Update SQLite
    print("Updating SQLite...")
    for u in update_queue:
        cur.execute("""
            UPDATE candidates 
            SET name_kr = ?, phone = ?, email = ?, current_company = ?, is_neo4j_synced = 0 
            WHERE id = ?
        """, (u['name_kr'], u['phone'], u['email'], u['current_company'], u['id']))
    conn.commit()
    print("Done SQLite Update.")
    
    # 2. Update AuraDB
    print("Updating AuraDB...")
    uri = 'neo4j+ssc://72de4959.databases.neo4j.io'
    driver = GraphDatabase.driver(uri, auth=('72de4959', 'oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns'))
    try:
        with driver.session() as s:
            q = """
            UNWIND $batch AS b
            MATCH (c:Candidate {id: b.id})
            SET c.name_kr = b.name_kr,
                c.name = b.name_kr,
                c.phone = b.phone,
                c.email = b.email,
                c.current_company = b.current_company
            """
            s.run(q, batch=update_queue)
        print("Done AuraDB Update.")
    except Exception as e:
        print("AuraDB error:", e)
    finally:
        driver.close()
        
    # 3. Update Local Neo4j
    print("Updating Local Neo4j...")
    try:
        local_driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
        with local_driver.session() as s:
            s.run(q, batch=update_queue)
        local_driver.close()
        print("Done Local Neo4j Update.")
    except Exception:
        print("Local Neo4j might be offline or failed. Skipping.")
        
conn.close()
print("All set!")
