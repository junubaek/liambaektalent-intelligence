import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect('candidates.db')
c = con.cursor()

query = '''
SELECT 
  a.name_kr,
  a.id as ghost_id,
  a.is_duplicate,
  a.duplicate_of,
  b.id as keeper_id,
  b.raw_text as summary
FROM candidates a
LEFT JOIN candidates b 
  ON b.document_hash = a.duplicate_of AND b.is_duplicate = 0
WHERE a.name_kr IN (
  '이준호', '이새은', '김민지', '김현준', 
  '박지민', '강동현', '강건규', '김지훈'
)
AND a.is_duplicate = 1
LIMIT 20;
'''

c.execute(query)
rows = c.fetchall()

has_issues = False
print(f"Total matched cross-check records: {len(rows)}")

for r in rows:
    name, ghost_id, is_duplicate, duplicate_of, keeper_id, summary = r
    
    issue_msgs = []
    if not duplicate_of:
        issue_msgs.append("duplicate_of IS NULL")
        
    if not keeper_id:
        issue_msgs.append(f"keeper_id IS NULL (Hash {duplicate_of} not found in active records)")
        
    if keeper_id and (not summary or len(summary) < 50):
        issue_msgs.append("keeper has empty or too short summary")
        
    if issue_msgs:
        has_issues = True
        print(f"ISSUE FOUND: Name={name}, Ghost={ghost_id} -> {issue_msgs}")
    else:
        print(f"OK: Name={name}, Ghost={ghost_id[:8]}... -> Keeper={keeper_id[:8]}... (Summary Len: {len(summary)})")

if has_issues:
    print("\n[RESULT] Issues found during cross-check! Aborting deletion.")
else:
    print("\n[RESULT] No issues found. SQLite Deduplication logic is valid.")
