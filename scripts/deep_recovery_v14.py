import sys
import json
import logging
import time

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB
from connectors.gemini_api import GeminiClient
from connectors.gdrive_api import GDriveConnector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PRIMARY_SECTORS = ['HW', '기타', 'SW', '마케팅', 'PRODUCT', '반도체', '디자인', 'HR']
DOMAINS = ['General / Other', 'AI / ML', 'E-commerce', 'Media / Content', 'Healthcare / Bio', 
           'SaaS / B2B', 'IoT / Hardware', 'Fintech', 'Blockchain / Web3', 'Game', 'Edutech', 
           'Mobility / Logistics', 'O2O / Platform', 'Real Estate / Proptech', 'Adtech', 'Travel / Hospitality']

PROMPT = """You are an expert Headhunter Data Encoder.
Based on the following full candidate resume, output a strictly valid JSON exactly matching the requested keys.
Do NOT include markdown formatting like ```json.

[Schema]
1. "Primary Sector": Must be EXACTLY ONE from this list: {primary}
2. "Domain": Must be a LIST of UP TO TWO strings exactly from this list: {domains}. If none fit, use "General / Other".
3. "Experience_Summary": A concise professional summary (3-4 bullet points) in Korean, summarizing overall career and core strength.
4. "Functional Patterns": Extract exactly 3 to 6 factual business/functional keywords. Follow the exact rules:
   - NO subjective words (Successfully, Led, 총괄 등).
   - Use English nouns/gerunds.
   - Append `_Exp` for features/roles, `_Env` for environments/stacks, `_Process` for methodologies.
   - Examples: Payment_System_Exp, Python_Env, Agile_Process.

[Resume Text]
{text}
"""

def main():
    try:
        with open(f"{PROJECT_ROOT}/secrets.json", "r", encoding="utf-8") as f:
            secrets = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return

    db = HeadhunterDB(f"{PROJECT_ROOT}/secrets.json")
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    gconnector = GDriveConnector()
    
    logger.info("Fetching candidates marked with No_Data_Processed...")
    filter_crit = {"property": "Functional Patterns", "multi_select": {"contains": "No_Data_Processed"}}
    cands = db.fetch_candidates(limit=5000, filter_criteria=filter_crit)
    
    logger.info(f"Found {len(cands)} candidates to recover.")
    
    for c in cands:
        name = c.get('이름', 'Unknown')
        link = c.get('구글드라이브_링크', '')
        cid = c['id']
        logger.info(f"\n[*] Processing: {name}")
        
        if not link:
            logger.warning(f"  ⏭️ No Google Drive link found for {name}. Cannot deep recover.")
            continue
            
        text = gconnector.extract_text_from_url(link)
        if not text:
            logger.warning(f"  ⏭️ Failed to extract text from GDrive link for {name}.")
            continue
            
        logger.info(f"  ✅ Extracted {len(text)} characters from GDrive.")
        
        prompt = PROMPT.format(
            primary=json.dumps(PRIMARY_SECTORS, ensure_ascii=False),
            domains=json.dumps(DOMAINS, ensure_ascii=False),
            text=text[:60000]  # Deep read up to 60k chars
        )
        
        try:
            res = gemini.get_chat_completion_json(prompt, model="gemini-2.5-flash")
            if not res:
                logger.error(f"  ❌ Gemini returned empty JSON.")
                continue
                
            p_sector = res.get("Primary Sector", "")
            domain = res.get("Domain", [])
            summary = res.get("Experience_Summary", "")
            patterns = res.get("Functional Patterns", [])
            
            if "No_Data_Processed" in patterns:
                patterns.remove("No_Data_Processed")
                
            props = {
                "Functional Patterns": {"multi_select": [{"name": p.replace(",", "/")} for p in patterns]},
                "Experience_Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]}
            }
            if p_sector in PRIMARY_SECTORS:
                props["Primary Sector"] = {"select": {"name": p_sector}}
            
            valid_domains = [d for d in (domain if isinstance(domain, list) else [domain]) if d in DOMAINS]
            if valid_domains:
                props["Domain"] = {"multi_select": [{"name": d} for d in valid_domains]}
                
            db.update_candidate(cid, props)
            logger.info(f"  ✅ Notion updated -> Primary: {p_sector}, Patterns: {patterns}")
            
        except Exception as e:
            logger.error(f"  ❌ Error during processing {name}: {e}")
            
        time.sleep(1) # rate limiting

if __name__ == "__main__":
    main()
