import json
# Supports both OpenAI and Gemini clients

import os
import sys

# Add parent to path for normalization import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from headhunting_engine.normalization.pattern_merger import PatternMerger

class JDParserV3:
    """
    JD Parser v3: Extracts 7-axis recruitment signals from raw JD text.
    v6.3.6: Integrated with Strategic Pattern Merger.
    """
    def __init__(self, client, ontology_path: str):
        self.client = client
        self.merger = PatternMerger()
        with open(ontology_path, 'r', encoding='utf-8') as f:
            self.ontology = json.load(f)

    def parse_jd(self, jd_text: str) -> dict:
        sectors_list = list(self.ontology["sectors"].keys())
        all_patterns = []
        for s in sectors_list:
            all_patterns.extend(self.ontology["sectors"][s]["patterns"])
        all_patterns = sorted(list(set(all_patterns)))

        prompt = f"""
You are a Senior Strategic Headhunter AI. Your task is to extract high-precision recruitment signals from a Job Description (JD) using the AI Talent Intelligence OS v6.3.4 Universal Ontology.

[CRITICAL: ONTOLOGY-ONLY MAPPING & CONSOLIDATION]
- EXCLUDE SOFT SKILLS: Completely ignore terms like Communication, Teamwork, Leadership (as an attitude), Passion, Sincerity, Collaboration, Problem Solving (as an attitude).
- MAPPING: Map all extracted requirements to the most relevant high-level functional category from the ontology.
- LIMITATION: Provide ONLY the top 7 most definitive and relevant functional patterns.
- FOCUS ON HARD SKILLS: Extract specific tools, frameworks, and protocols.
- FOCUS ON FUNCTIONAL PATTERNS: Extract concrete business or technical requirements and outcomes.

[9-SECTOR STRUCTURE]
Sectors: {", ".join(sectors_list)}

[MATCHING RULES: STRATEGIC FUNCTIONALITY]
1. Prioritize FUNCTIONAL OBJECTIVES over Abstract Descriptions. 
   - If JD mentions "KPI", "Strategy", "Insights" -> Sector: CORPORATE/DATA_AI. 
   - Focus on hard deliverables: "Metrics Framework", "Product Analytics", "Yield Optimization".
2. Cross-Sector Flag: If the role bridges two worlds (e.g., AI + Semiconductor, Finance + Tech), set `cross_sector_flag` to true.

[7-AXIS EXTRACTION RULES]
...
[JD TEXT]
{jd_text[:8000]}

[OUTPUT_FORMAT_JSON]
{{
  "jd_profile": {{
    "job_title": "",
    "primary_sector": "",
    "is_new_trend_detected": false
  }},
  "secondary_sectors": [],
  "cross_sector_flag": false,
  "seniority_required": 0,
  "leadership_level": "",
  "functional_domains": [],
  "must_patterns": [],
  "experience_patterns": [],
  "discovered_demands": [],
  "impact_requirements": {{}},
  "hard_constraints": []
}}
"""
        try:
            # Detect client type and use appropriate method
            if hasattr(self.client, "get_chat_completion_json"):
                # Both our OpenAIClient and GeminiClient now have this method
                parsed_data = self.client.get_chat_completion_json(prompt)
            else:
                parsed_data_str = self.client.get_chat_completion("You are an expert", prompt)
                parsed_data = json.loads(parsed_data_str) if isinstance(parsed_data_str, str) else parsed_data_str

            # v6.3.6 Strategic Merging for Demand-Side Consistentcy
            if "must_patterns" in parsed_data:
                parsed_data["must_patterns"] = self.merger.merge_list(parsed_data["must_patterns"], limit=7)
            if "experience_patterns" in parsed_data:
                parsed_data["experience_patterns"] = self.merger.merge_list(parsed_data["experience_patterns"], limit=7)
            
            return parsed_data
        except Exception as e:
            print(f"❌ JD Parser v3 Error: {e}")
            return {
                "jd_profile": {
                    "job_title": "Unclassified",
                    "primary_sector": "Unclassified",
                    "is_new_trend_detected": False
                },
                "secondary_sectors": [],
                "cross_sector_flag": False,
                "seniority_required": 0,
                "leadership_level": "IC",
                "functional_domains": [],
                "must_patterns": [],
                "experience_patterns": [],
                "impact_requirements": {},
                "hard_constraints": ["Parsing Error"],
                "discovered_demands": []
            }

if __name__ == "__main__":
    # Test stub (requires API Key)
    pass
