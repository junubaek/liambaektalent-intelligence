import json
import sqlite3
import os

CACHE_FILE = "candidates_cache_jd.json"
DB_FILE = "candidates.db"

def migrate():
    print(f"🚀 Starting Migration from {CACHE_FILE} to {DB_FILE}...")
    
    if not os.path.exists(CACHE_FILE):
        print(f"❌ {CACHE_FILE} not found!")
        return
        
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Table based on spec
    # Added id as text to link directly to Notion/Neo4j
    # Added parsed_career_json to hold the structured array
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT,
            name_kr TEXT,
            phone TEXT,
            email TEXT,
            summary TEXT,
            profile_summary TEXT,
            current_company TEXT,
            sector TEXT,
            seniority TEXT,
            total_years REAL,
            parsed_career_json TEXT
        )
    """)
    
    # Clear existing if re-running
    cursor.execute("DELETE FROM candidates")
    
    success = 0
    fail = 0
    
    for c in data:
        # Prevent primary key NULL errors
        cid = c.get("id")
        if not cid: continue
        
        try:
            cursor.execute("""
                INSERT INTO candidates (
                    id, name, name_kr, phone, email, summary, profile_summary, 
                    current_company, sector, seniority, total_years, parsed_career_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid,
                c.get("name", ""),
                c.get("name_kr", ""),
                c.get("phone", ""),
                c.get("email", ""),
                c.get("summary", ""),
                c.get("profile_summary", ""),
                c.get("current_company", ""),
                ", ".join(c.get("main_sectors", [])) if isinstance(c.get("main_sectors"), list) else c.get("sector", ""),
                c.get("seniority", ""),
                c.get("total_years", 0.0),
                json.dumps(c.get("parsed_career_json", []), ensure_ascii=False) if c.get("parsed_career_json") else None
            ))
            success += 1
        except Exception as e:
            print(f"❌ Error inserting {c.get('name')}: {e}")
            fail += 1
            
    conn.commit()
    conn.close()
    
    print(f"\n✨ SQLite Migration Complete!")
    print(f"   - Success: {success}")
    print(f"   - Failed: {fail}")
    print(f"   - Total rows in {DB_FILE}: {success}")

if __name__ == "__main__":
    migrate()
