import os
import time
import json
from sqlalchemy import text
from app.database import SessionLocal
from connectors.notion_api import HeadhunterDB

def main():
    print("Starting Round 2 Google Drive URL Backfill (Expanded Conditions)...")
    db = SessionLocal()
    notion = HeadhunterDB()

    try:
        # Get targets
        q = """
        SELECT id, name_kr 
        FROM candidates 
        WHERE is_duplicate=0 
        AND (google_drive_url IS NULL OR google_drive_url = '' OR google_drive_url = '#')
        """
        targets = db.execute(text(q)).fetchall()
        print(f"🎯 Targets to process: {len(targets)}")

        success_count = 0
        no_url_count = 0

        for i, (cid, name) in enumerate(targets):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(targets)} | Found: {success_count} | Empty: {no_url_count}")

            try:
                # Notion API request
                page_data = notion.client._request("GET", f"pages/{cid}")
                if not page_data or 'error' in page_data or page_data.get('object') == 'error':
                    no_url_count += 1
                    time.sleep(0.4)
                    continue

                props = page_data.get("properties", {})
                
                drive_url = None
                for prop_name, prop_data in props.items():
                    ptype = prop_data.get("type", "")
                    
                    if ptype == "url":
                        val = prop_data.get("url")
                        if val and ("drive.google.com" in val or "docs.google.com" in val or "sheets.google.com" in val):
                            drive_url = val
                            break
                            
                    elif ptype == "files":
                        for f in prop_data.get("files", []):
                            if f.get("type") == "external":
                                val = f.get("external", {}).get("url", "")
                                if val and ("drive.google.com" in val or "docs.google.com" in val or "sheets.google.com" in val):
                                    drive_url = val
                                    break
                
                if drive_url:
                    db.execute(text("UPDATE candidates SET google_drive_url = :url WHERE id = :cid"), {"url": drive_url, "cid": cid})
                    db.commit()
                    success_count += 1
                else:
                    no_url_count += 1
            except Exception as e:
                # Page not found or archived
                print(f"[Warn] Error fetching {name} ({cid}): {e}")
                
            time.sleep(0.4) # Rate limit

        print(f"\n✨ Round 2 Backfill Complete! Newly acquired: {success_count} | Still missing: {no_url_count}")
        
        # Verify final statistics
        print("\n--- Final Database Status ---")
        res = db.execute(text("""
        SELECT 
          COUNT(*) as total,
          SUM(CASE WHEN google_drive_url IS NOT NULL 
                   AND google_drive_url != '' 
                   AND google_drive_url != '#' 
              THEN 1 ELSE 0 END) as has_drive,
          SUM(CASE WHEN google_drive_url IS NULL 
                   OR google_drive_url = '' 
                   OR google_drive_url = '#' 
              THEN 1 ELSE 0 END) as no_drive
        FROM candidates
        WHERE is_duplicate=0;
        """)).fetchone()
        
        total, has_d, no_d = res
        print(f"Total Active Candidates: {total}")
        print(f"With Drive URL: {has_d} ({round(has_d/total*100, 1)}%)")
        print(f"Without Drive URL: {no_d} ({round(no_d/total*100, 1)}%)")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
