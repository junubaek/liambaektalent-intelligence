import time
import sqlite3
import os
import subprocess

def wait_and_audit():
    conn = sqlite3.connect("candidates.db")
    while True:
        c = conn.cursor()
        unsynced = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND is_pinecone_synced=0").fetchone()[0]
        if unsynced == 0:
            print("Successfully synced all limbo candidates to Pinecone!")
            break
        print(f"Waiting for {unsynced} candidates to sync to Pinecone...")
        time.sleep(5)
        
    print("Running system_auditor.py...")
    # Run auditor with utf-8 encoding forcefully
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(["python", "system_auditor.py"], env=env, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)

if __name__ == "__main__":
    wait_and_audit()
