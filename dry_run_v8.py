
import json
import os
import sys

# Define base project path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser
from classification_rules import get_role_cluster

def run_dry_run():
    # Load secrets using absolute path
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(client)
    
    # Sample candidate text (Simulating a Senior HW/Semiconductor engineer per Rule 3)
    test_resume = """
    Name: Kim Ji-Hoon
    Experience: 12 years
    Recent: Principal Engineer at NVIDIA (Semiconductor Division)
    Past: Senior Lead at Samsung LSI.
    Skills: SoC Design, RTL Verification, UVM, Verilog, C++.
    Education: MS in Electrical Engineering.
    Achievements: Led 5nm tape-out for AI Accelerator. System architect for high-speed I/O.
    """
    
    print("--- [v8.0] Dry Run: Resume Analysis ---")
    result = parser.parse(test_resume)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result:
        profile = result.get("candidate_profile", {})
        primary = profile.get("primary_sector")
        bucket = profile.get("seniority_bucket")
        
        print(f"\n[Verification Results]")
        print(f"- Primary Sector: {primary}")
        print(f"- Seniority Bucket: {bucket}")
        
        cluster = get_role_cluster(primary)
        print(f"- Cluster Verification (v8.0): {cluster}")

if __name__ == "__main__":
    run_dry_run()
