import os
import shutil
import datetime
import json
import subprocess

def run_night_job():
    print("=== Nighttime Parsing & Evaluation Job Started ===")
    
    # 1. Backup processed.json
    if os.path.exists("processed.json"):
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        backup_name = f"processed_backup_phase3_{date_str}.json"
        shutil.copy("processed.json", backup_name)
        print(f"Backed up processed.json to {backup_name}")
        
        # Ensure processed.json is empty to force re-parsing
        with open("processed.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        print("Cleared processed.json for full re-parsing.")
    
    # 2. Modify dynamic_parser_v2.py to delete edges right before replacing (to avoid empty gaps)
    with open("dynamic_parser_v2.py", "r", encoding="utf-8") as f:
        parser_text = f.read()
        
    old_target = "target_id = node_id if node_id else document_hash"
    new_target = "target_id = node_id if node_id else document_hash\n            session.run(\"MATCH (c:Candidate {id: $id})-[r]->() DELETE r\", id=target_id)"
    
    if "DELETE r" not in parser_text:
        parser_text = parser_text.replace(old_target, new_target)
        with open("dynamic_parser_v2.py", "w", encoding="utf-8") as f:
            f.write(parser_text)
        print("Patched dynamic_parser_v2.py for sequential edge overwrite.")

    # 3. Run Parser
    print("Launching dynamic_parser_v2.py ... (This will take a long time)")
    subprocess.run(["python", "dynamic_parser_v2.py"], env=os.environ.copy())
    
    # 4. Generate basic statistics
    # You can read processed.json to see how many were parsed
    try:
        with open("processed.json", "r", encoding="utf-8") as f:
            proc_data = json.load(f)
            print(f"\n[Report] Total candidates parsed successfully: {len(proc_data)}")
    except Exception as e:
        print(f"[Error] Failed to read processed.json for stats: {e}")
        
    # 5. Run Evaluation
    eval_script = "run_real_evaluate_v4.py"
    if not os.path.exists(eval_script):
        eval_script = "run_real_evaluate_v3.py"
        
    print(f"Launching Evaluation: {eval_script} ...")
    subprocess.run(["python", eval_script], env=os.environ.copy())
    
    print("=== Nighttime Job Completed ===")

if __name__ == "__main__":
    run_night_job()
