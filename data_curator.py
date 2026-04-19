
import json
import logging
import os
from connectors.notion_api import HeadhunterDB, NotionClient
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import difflib
from backend.ontologist import KeywordOntologist

# Curator가 새 패턴을 추가하기 전 체크 (100개 제한 방어 로직)
def add_pattern_safe(new_pattern: str, existing_patterns: list) -> str:
    if len(existing_patterns) >= 100:
        # 100개 초과 시 가장 유사한 기존 패턴으로 매핑
        matches = difflib.get_close_matches(new_pattern, existing_patterns, n=1, cutoff=0.3)
        if matches:
            return matches[0]
        # 유사 패턴마저 없으면 그냥 기존 패턴 중 첫 번째 것으로 Fallback (안전을 위해)
        return existing_patterns[0] if existing_patterns else new_pattern
    return new_pattern  # 100개 미만 여유 있으면 새 패턴으로 추가

class DataCurator:
    def __init__(self, secrets_path="secrets.json"):
        with open(secrets_path, "r", encoding="utf-8") as f:
            self.secrets = json.load(f)
        
        self.notion_db = HeadhunterDB(secrets_path)
        self.client = self.notion_db.client
        self.gemini = GeminiClient(self.secrets["GEMINI_API_KEY"])
        self.parser = ResumeParser(self.gemini)
        self.ontologist = KeywordOntologist(secrets_path)
        self._existing_patterns_cache = None
        
    def _get_existing_patterns(self) -> list:
        if self._existing_patterns_cache is not None:
            return self._existing_patterns_cache
            
        db_id = self.secrets.get("NOTION_DATABASE_ID")
        db_info = self.client._request("GET", f"databases/{db_id}")
        if db_info and "properties" in db_info and "Functional Patterns" in db_info["properties"]:
            options = db_info["properties"]["Functional Patterns"].get("multi_select", {}).get("options", [])
            self._existing_patterns_cache = [opt["name"] for opt in options]
        else:
            self._existing_patterns_cache = []
        return self._existing_patterns_cache

    def diagnose_db(self, limit=100):
        """Finds records with missing or low-quality data."""
        logger.info("Running DB Diagnostics (Python-side filtering)...")
        db_id = self.secrets.get("NOTION_DATABASE_ID")
        if not db_id:
            logger.error("NOTION_DATABASE_ID not found in secrets.json")
            return []
            
        res = self.client.query_database(db_id, limit=limit)
        all_pages = res.get('results', [])
        
        candidates_needing_repair = []
        for p in all_pages:
            props = self.client.extract_properties(p)
            sub_sectors = props.get('sub_sectors', [])
            experience_patterns = props.get('experience_patterns', [])
            
            # Criteria: Sub Sector is empty OR patterns are missing
            if not sub_sectors or not experience_patterns:
                candidates_needing_repair.append(props)
        
        logger.info(f"Identified {len(candidates_needing_repair)} candidates requiring attention (out of {len(all_pages)} scanned).")
        return candidates_needing_repair

    def repair_candidate(self, cand):
        """Re-parses a candidate and updates Notion."""
        cand_id = cand['id']
        name = cand.get('name') or "Unknown"
        logger.info(f"Repairing candidate: {name} ({cand_id})")
        
        # 1. Fetch full text
        full_text = self.notion_db.fetch_candidate_details(cand_id)
        if not full_text:
            logger.warning(f"No content found for {name}. Using summary if available.")
            full_text = cand.get('experience_summary', '')
            
        # 2. Parse via v8.0 Engine
        parsed = self.parser.parse(full_text)
        if not parsed:
            logger.error(f"Failed to parse {name}.")
            return False
            
        # 3. Process Properties (PROTECT Main Sectors)
        profile = parsed.get('candidate_profile', {})
        extracted_patterns = parsed.get('patterns', [])
        
        # 100-limit Safe Logic for Functional Patterns
        existing_patterns = self._get_existing_patterns()
        safe_patterns_to_upload = set()
        new_keywords = set()
        
        for pt in extracted_patterns:
            raw_pt = pt.get("verb_object", "")
            if raw_pt:
                # Add pattern safely
                safe_pt = add_pattern_safe(raw_pt, existing_patterns)
                safe_patterns_to_upload.add(safe_pt)
                
                # If it's a completely new pattern that was allowed in, track it
                if safe_pt not in existing_patterns:
                    existing_patterns.append(safe_pt)
                    
            # Pass extracted tools to Ontologist
            for tool in pt.get("tools", []):
                new_keywords.add(tool)
        
        # Also pass sub sectors to Ontologist
        for sub in profile.get('sub_sectors', []):
            new_keywords.add(sub)
            
        gap_signals = profile.get('gap_analysis', [])
        gap_text = "\n".join(gap_signals) if isinstance(gap_signals, list) else str(gap_signals)
            
        properties = {
            # 🚨 Main Sectors MUST NOT BE INCLUDED HERE (Absolute Constraint)
            "Sub Sectors": {"multi_select": [{"name": s} for s in profile.get('sub_sectors', [])]},
            "Functional Patterns": {"multi_select": [{"name": s} for s in list(safe_patterns_to_upload)[:20]]}, # Max 20 per person
            "Experience Summary": {"rich_text": [{"text": {"content": profile.get('experience_summary', '')[:2000]}}]},
            "Gap Analysis": {"rich_text": [{"text": {"content": gap_text[:2000]}}]} if gap_text else {"rich_text": []}
        }
        
        try:
            self.client.update_page_properties(cand_id, properties)
            logger.info(f"Successfully repaired and updated {name}. Protected Main Sectors.")
            
            # Run Ontologist strictly on the newly found terms
            if new_keywords:
                self.ontologist.process_new_keywords(list(new_keywords))
                
            return True
        except Exception as e:
            logger.error(f"Failed to update Notion for {name}: {e}")
            return False

    def run_clean_cycle(self, limit=50):
        """Main loop for the curator agent."""
        candidates = self.diagnose_db(limit=limit)
        repaired_count = 0
        for cand in candidates:
            if self.repair_candidate(cand):
                repaired_count += 1
                
        logger.info(f"Clean cycle complete. Repaired {repaired_count} candidates.")
        return repaired_count

if __name__ == "__main__":
    curator = DataCurator()
    # Execute a repair cycle
    curator.run_clean_cycle(limit=10)
