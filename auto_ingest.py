import subprocess
import sys

def run_pipeline():
    print("=== STARTING PHASE 1: Notion Upload (Skipping Duplicates) ===")
    try:
        subprocess.run([sys.executable, "pdf_to_notion.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Phase 1 failed: {e}")
        return

    print("\n=== STARTING PHASE 2: AI Candidate Analysis ===")
    try:
        subprocess.run([sys.executable, "main_ingest.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Phase 2 failed: {e}")
        return
        
    print("\n=== AUTOMATED INGESTION COMPLETE ===")

if __name__ == "__main__":
    run_pipeline()
