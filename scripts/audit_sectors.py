import os
import json
import random
import logging
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB
from connectors.gemini_api import GeminiClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

PRIMARY_SECTORS = ['HW', '기타', 'SW', '마케팅', 'PRODUCT', '반도체', '디자인', 'HR']
DOMAINS = ['General / Other', 'AI / ML', 'E-commerce', 'Media / Content', 'Healthcare / Bio', 
           'SaaS / B2B', 'IoT / Hardware', 'Fintech', 'Blockchain / Web3', 'Game', 'Edutech', 
           'Mobility / Logistics', 'O2O / Platform', 'Real Estate / Proptech', 'Adtech', 'Travel / Hospitality']

PROMPT = """
You are an expert Headhunter Auditor. 
You are given a candidate's resume text. You must accurately classify the candidate into one Primary Sector and up to two Domains based strictly on this allowed ontology:

[ALLOWED PRIMARY SECTORS]
{primary}

[ALLOWED DOMAINS]
{domains}

[RESUME TEXT]
{text}

Return ONLY a valid JSON dictionary indicating your choices. Do not explain. Example format:
{{
  "Primary Sector": "SW",
  "Domain": ["AI / ML", "E-commerce"]
}}
"""

def run_audit():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    db = HeadhunterDB()
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    
    logger.info("Fetching candidates that have a Primary Sector assigned...")
    filter_criteria = {"property": "Primary Sector", "select": {"is_not_empty": True}}
    cands = db.fetch_candidates(limit=50, filter_criteria=filter_criteria)
    
    valid_cands = [c for c in cands if c.get('primary_sector') and c.get('primary_sector') != 'Unclassified']
    
    if len(valid_cands) < 10:
        sample = valid_cands
    else:
        sample = random.sample(valid_cands, 10)
        
    logger.info(f"Selected {len(sample)} candidates for audit.\n")
    
    for c in sample:
        name = c.get('이름', 'Unknown')
        logger.info(f">> Starting audit for: {name}")
        old_primary = c.get('primary_sector', 'None')
        old_domains = c.get('domain', [])
        if isinstance(old_domains, str):
            old_domains = [old_domains]
            
        text = db.fetch_candidate_details(c['id'])
        if not text:
            logger.warning(f"  Skipping {name}: No text parsed.")
            continue
            
        logger.info(f"  Fetched {len(text)} characters of text. Contacting Gemini...")
        
        prompt = PROMPT.format(primary=json.dumps(PRIMARY_SECTORS, ensure_ascii=False), 
                               domains=json.dumps(DOMAINS, ensure_ascii=False), 
                               text=text[:10000])
                               
        res = gemini.get_chat_completion_json(prompt)
        if not res:
            logger.error(f"  Gemini returned empty or invalid JSON for {name}.")
            continue
        
        ai_primary = res.get("Primary Sector", "")
        ai_domains = res.get("Domain", [])
        if isinstance(ai_domains, str):
            ai_domains = [ai_domains]
            
        logger.info(f"--- Candidate: {name} ---")
        logger.info(f"  Current DB -> Primary: {old_primary} | Domain: {old_domains}")
        logger.info(f"  AI Auditor -> Primary: {ai_primary} | Domain: {ai_domains}")
        
        # Check alignment
        p_match = (old_primary == ai_primary)
        d_match = bool(set(old_domains).intersection(set(ai_domains))) or (not old_domains and not ai_domains)
        
        if p_match and d_match:
            logger.info("  Result: PERFECT MATCH ✅")
        elif p_match:
            logger.info("  Result: PARTIAL MATCH (Primary OK) ⚠️")
        else:
            logger.info("  Result: MISMATCH ❌")
        logger.info("")

if __name__ == "__main__":
    run_audit()
