import json
import os
import logging
from connectors.gemini_api import GeminiClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SYNONYMS_FILE = os.path.join(ROOT_DIR, "synonyms.json")
SECRETS_FILE = os.path.join(os.path.dirname(ROOT_DIR), "secrets.json")

class KeywordOntologist:
    def __init__(self, secrets_path: str = SECRETS_FILE):
        if not os.path.exists(secrets_path):
            secrets_path = os.path.join(ROOT_DIR, "secrets.json") # Fallback
            
        with open(secrets_path, "r", encoding="utf-8") as f:
            secrets = json.load(f)
            
        self.gemini = GeminiClient(secrets["GEMINI_API_KEY"])
        self.synonym_groups = self._load_synonyms()

    def _load_synonyms(self):
        if os.path.exists(SYNONYMS_FILE):
            with open(SYNONYMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_synonyms(self):
        with open(SYNONYMS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.synonym_groups, f, ensure_ascii=False, indent=4)

    def process_new_keywords(self, keywords: list[str]):
        """Agent 3 Main Loop: Clusters newly found keywords into the SYNONYM_GROUPS."""
        if not keywords:
            return 0
            
        # Filter raw keywords to only those not already in the groups
        existing_words = {word.lower() for group in self.synonym_groups for word in group}
        new_words = [kw for kw in keywords if kw.lower() not in existing_words and len(kw.strip()) >= 2]
        
        if not new_words:
            logger.info("No completely new keywords to process.")
            return 0
            
        logger.info(f"Ontologist analyzing {len(new_words)} new keywords: {new_words}")
        
        # Build prompt for Gemini to classify these new keywords
        groups_str = "\n".join([f"Group {i}: {', '.join(g[:3])}..." for i, g in enumerate(self.synonym_groups)])
        
        prompt = f"""
You are the Keyword Ontologist AI. Your job is to classify new job-related keywords into existing synonym groups.

[EXISTING GROUPS]
{groups_str}

[NEW KEYWORDS TO CLASSIFY]
{json.dumps(new_words, ensure_ascii=False)}

[TASK]
For each new keyword, determine if it closely belongs to one of the EXISTING GROUPS.
If it is a perfect synonym or highly relevant related term for an existing group, assign it the Group ID integer.
If it is completely unrelated to any group, assign it a Group ID of -1 (we will create a new group for it).

Output exactly in this JSON format:
{{
  "classification": [
    {{"keyword": "str", "group_id": int}}
  ]
}}
"""
        added_count = 0
        try:
            res = self.gemini.get_chat_completion_json(prompt, model="gemini-3.0-flash-preview")
            classifications = res.get("classification", [])
            
            for item in classifications:
                kw = item.get("keyword")
                gid = item.get("group_id")
                
                if kw not in new_words:
                    continue
                    
                if gid != -1 and 0 <= gid < len(self.synonym_groups):
                    self.synonym_groups[gid].append(kw)
                    logger.info(f"Added '{kw}' to Group {gid}")
                    added_count += 1
                elif gid == -1:
                    self.synonym_groups.append([kw])
                    logger.info(f"Created new Group {len(self.synonym_groups)-1} for '{kw}'")
                    added_count += 1
                    
            if added_count > 0:
                self._save_synonyms()
                logger.info(f"Ontologist successfully incorporated {added_count} new keywords into synonyms.json")
                
        except Exception as e:
            logger.error(f"Ontology clustering failed: {e}")
            
        return added_count
