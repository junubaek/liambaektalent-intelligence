
import json
import os
from connectors.openai_api import OpenAIClient

class JDAnalyzerV5:
    def __init__(self, openai_client):
        self.openai = openai_client
        # Load Universal Ontology
        ontology_path = os.path.join(os.path.dirname(__file__), "headhunting_engine/universal_ontology.json")
        try:
            with open(ontology_path, "r", encoding="utf-8") as f:
                self.ontology = json.load(f)
        except:
            self.ontology = {}

    def analyze(self, jd_text: str) -> dict:
        """
        [v6.0] Discovery-First Extraction Engine
        Prioritizes literal JD text and separates Explicit vs Inferred signals.
        """
        # Collect allowed legacy patterns for fallback compatibility
        allowed_patterns = []
        for sector_data in self.ontology.get("sectors", {}).values():
            allowed_patterns.extend(sector_data.get("patterns", []))
        allowed_patterns = sorted(list(set(allowed_patterns)))

        system_prompt = """
You are a JD Intelligence Extraction Engine (v6.0 Discovery-First).
Your goal is to extract literal signals from JD text without forcing them into narrow patterns.

[PHASE 1: LITERAL EXTRACTION]
- role_family: The dominant professional category (e.g., Data Analyst, SW Engineer).
- explicit_must_haves: Tools, skills, or behaviors mentioned EXPLICITLY as required (e.g., SQL, KPI 트래킹).
- explicit_background: Industry or team context mentioned literally (e.g., Strategy Team).

[PHASE 2: INFERRED CONTEXT]
- seniority_required: Years of experience. If NOT explicit, set to 0 and mark as inferred.
- leadership_level: IC | Lead | Executive. If NOT explicit, mark as inferred.
- inferred_patterns: Map JD to English patterns ONLY if they fit closely. 
  Allowed Patterns: """ + ", ".join(allowed_patterns) + """

[PHASE 3: SEARCH STRATEGY]
- search_broad_category: A broad, high-recall category name for initial candidate pool recruitment.

[LANGUAGE RULE]
- Extract 'role_family', 'explicit_must_haves', and 'explicit_background' in the language of the JD (Korean if JD is Korean).
- 'inferred_patterns' MUST ALWAYS be in English.

Output JSON Format:
{
  "role_family": "Korean Name",
  "search_broad_category": "Main Category Name",
  "explicit_must_haves": ["Signal 1", ...],
  "explicit_tools": ["Tool 1", ...],
  "explicit_background": "Context",
  "seniority": {
     "value": 0,
     "is_inferred": true
  },
  "leadership": {
     "level": "Individual Contributor",
     "is_inferred": true
  },
  "inferred_patterns": ["Pattern1", ...],
  "provenance": [
    {"signal": "Signal name", "source_sentence": "Original sentence from JD"}
  ]
}
"""
        user_prompt = "Analyze this JD for Discovery-First Matching:\n" + jd_text[:8000]
        
        try:
            response = self.openai.get_chat_completion(system_prompt, user_prompt)
            clean_json = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            # --- V5 Compatibility Layer (Crucial for existing Matcher/UI) ---
            data["canonical_role"] = data.get("role_family", "Unknown")
            data["must_skills"] = data.get("explicit_must_haves", []) + data.get("explicit_tools", [])
            data["functional_domains"] = data["must_skills"]
            data["hard_constraints"] = data["must_skills"]
            data["role"] = data["canonical_role"]
            data["leadership_level"] = data.get("leadership", {}).get("level", "IC")
            data["seniority_required"] = data.get("seniority", {}).get("value", 0)
            data["experience_patterns"] = data.get("inferred_patterns", [])
            
            # Signal Metadata for UI (Transparency)
            data["discovery_metadata"] = {
                "broad_search_trigger": data.get("search_broad_category", data["canonical_role"]),
                "explicit_count": len(data.get("explicit_must_haves", [])),
                "inferred_signals": ["seniority", "leadership"] if data.get("seniority", {}).get("is_inferred") else []
            }
            
            return data
        except Exception as e:
            print(f"JD Analyzer V5 Error: {e}")
            return {"domain": "Unknown", "patterns": [], "must_skills": []}
