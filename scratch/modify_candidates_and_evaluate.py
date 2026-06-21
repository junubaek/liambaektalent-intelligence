import sqlite3, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

def apply_updates(db_path='candidates.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # 배유정 sector change
    cur.execute("UPDATE candidates SET sector='Marketing' WHERE name_kr='배유정' AND is_duplicate=0")
    print('배유정 sector updated:', cur.rowcount)
    # 강건규 duplicate handling
    cur.execute("""
        UPDATE candidates SET is_duplicate=1
        WHERE name_kr='강건규'
        AND (email IS NULL OR email='')
        AND (total_years=0 OR total_years IS NULL)
        AND is_duplicate=0
    """)
    print('강건규 duplicate updated:', cur.rowcount)
    # 배문성 sector change
    cur.execute("UPDATE candidates SET sector='Operations' WHERE name_kr='배문성' AND is_duplicate=0")
    print('배문성 sector updated:', cur.rowcount)
    conn.commit()
    conn.close()

def run_ndcg():
    # Assuming scratch_eval_ndcg.py is in the project root
    proc = subprocess.run(['python', 'scratch_eval_ndcg.py'], capture_output=True, text=True)
    print('NDCG Evaluation Output:')
    print(proc.stdout)
    if proc.stderr:
        print('Errors:', proc.stderr, file=sys.stderr)

if __name__ == '__main__':
    apply_updates()
    run_ndcg()
