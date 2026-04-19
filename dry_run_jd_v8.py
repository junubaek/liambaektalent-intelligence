
import json
import os
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gemini_api import GeminiClient
from jd_analyzer_v8 import JDAnalyzerV8

def run_jd_dry_run():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets["GEMINI_API_KEY"])
    analyzer = JDAnalyzerV8(client)
    
    test_jd = """
    Job Title: Senior AI System Architect
    Company: TechFrontiers
    Description:
    We are looking for an expert to design next-generation AI accelerators.
    Role involves SoC architecture design and optimization for deep learning workloads.
    Experience with HBM3 interface and CXL protocol is a must.
    Looking for someone who can lead a team of 10+ RTL engineers.
    """
    
    print("--- [v8.0] Dry Run: JD Analysis ---")
    result = analyzer.analyze(test_jd)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result:
        print("\n[Verification Results]")
        print(f"- Primary Sector: {result.get('primary_sector')}")
        print(f"- Context Tags: {result.get('context_tags')}")

if __name__ == "__main__":
    run_jd_dry_run()
