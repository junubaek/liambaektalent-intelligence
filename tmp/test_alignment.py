
import json
import os
from connectors.openai_api import OpenAIClient
from jd_analyzer_v4 import JDAnalyzerV4

def test_alignment():
    # Load secrets
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    analyzer = JDAnalyzerV4(openai)
    
    # Sample JD (Business/Finance)
    jd_text = """
    We are looking for a Senior Finance Manager.
    Experience in financial modeling, budgeting, and forecasting is a must.
    Experience in M&A due diligence and deal structuring is highly preferred.
    Expected to lead a team of 3.
    """
    
    print("Testing JD Analyzer V4...")
    result = analyzer.analyze(jd_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Load candidate patterns from report (simulated check)
    # We want to see if the extracted patterns match what we have in the database.
    print("\nComparing with candidate patterns...")
    extracted_patterns = result.get("experience_patterns", [])
    
    # Just a manual check for now
    print(f"Extracted Patterns: {extracted_patterns}")

if __name__ == "__main__":
    test_alignment()
