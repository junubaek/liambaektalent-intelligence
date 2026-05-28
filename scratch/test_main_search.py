import sqlite3
import json
import os
import sys

# Add backend directory to path to import
sys.path.append(os.path.abspath('backend'))
sys.path.append(os.path.abspath('.'))

from jd_compiler import get_candidates_from_cache

# 1. Let's see what get_candidates_from_cache returns for them
all_cands = get_candidates_from_cache()
cand_dict = {str(c.get('id')): c for c in all_cands}

names = ['김국현', '우형일', '황의영']

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for name in names:
    cur.execute('''
        SELECT id, name_kr, current_company, sector, profile_summary, google_drive_url, total_years
        FROM candidates
        WHERE name_kr=? AND is_duplicate=0
    ''', (name,))
    row = cur.fetchone()
    if not row:
        print(f"Candidate {name} not found in SQLite.")
        continue
        
    cid = str(row["id"])
    c = cand_dict.get(cid, {})
    
    print(f"\n--- Candidate: {name} ---")
    print("SQLite row details:")
    print("  sector:", row["sector"])
    print("  company:", row["current_company"])
    print("  summary:", row["profile_summary"][:100] if row["profile_summary"] else None)
    
    print("Cache 'c' details:")
    print("  c.get('id'):", c.get('id'))
    print("  c.get('name'):", c.get('name'))
    print("  c.get('current_company'):", c.get('current_company'))
    print("  c.get('main_sectors'):", c.get('main_sectors'))
    print("  c.get('profile_summary'):", c.get('profile_summary'))
    
    # Let's mimic the result dictionary construction from backend/main.py
    constructed = {
        "id": cid,
        "name": row["name_kr"] or c.get("name_kr") or c.get("name") or "이름 없음",
        "current_company": c.get("current_company") or row["current_company"] or "미지정",
        "sector": (c.get("main_sectors", ["미분류"])[0] if c.get("main_sectors") else None) or row["sector"] or "미분류",
        "profile_summary": c.get("profile_summary") or row["profile_summary"] or "",
        "google_drive_url": c.get("google_drive_url") or row["google_drive_url"] or ""
    }
    print("Constructed search result dictionary:")
    print("  sector:", constructed["sector"])
    print("  current_company:", constructed["current_company"])
    print("  profile_summary:", constructed["profile_summary"][:100] if constructed["profile_summary"] else None)

conn.close()
