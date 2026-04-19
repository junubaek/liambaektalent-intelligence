import json
import time
import sys
import os

sys.path.append(os.getcwd())
from connectors.gemini_api import GeminiClient

def complete_mapping():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)

    gemini = GeminiClient(secrets["GEMINI_API_KEY"])

    with open("current_patterns.json", "r", encoding="utf-8") as f:
        all_patterns = json.load(f)
        
    with open("pattern_mapping.json", "r", encoding="utf-8") as f:
        current_mapping = json.load(f)

    missing_patterns = [p for p in all_patterns if p not in current_mapping]
    print(f"Found {len(missing_patterns)} missing patterns to map.")

    if not missing_patterns:
        return

    PROMPT_TEMPLATE = """
You are an expert Talent Intelligence AI. Your task is to clean, standardize, and consolidate a list of raw resume "Functional Patterns".

[THE PROBLEM]
Many old patterns contain subjective words (ex: "총괄", "성공적으로", "Led", "Master") or performance figures (ex: "Achieved 20,000 users"). 
We must remove all subjectivity and metrics, keeping ONLY pure, factual environmental or process exposures.

[STRICT CLEANING RULES]
1. REMOVE SUBJECTIVITY: Strip words like "Led", "Successfully", "Managed", "총괄", "성공", "수행", "주도". We only care ABOUT what they were exposed to, not how well they did it.
2. REMOVE METRICS/AMOUNTS: Strip "20,000 users", "192 billion KRW", "4배 증대", "16개사". If the amount is removed but the core function remains, map it to the core function.
3. STANDARDIZED SUFFIX: Every mapped pattern MUST end with one of these factual suffixes: "_Exp" (Experience), "_Env" (Environment), "_Process", "_Cycle".
4. ENGLISH SNAKE_CASE: The mapped pattern MUST be in English, joined by underscores (e.g., `Marketing_Data_Analysis_Exp`). No commas allowed. No spaces allowed. Use slashes (/) only if strictly necessary.
5. CONSOLIDATE: If two raw patterns describe the same factual core (e.g. "마케팅 데이터 분석", "Marketing Data Analytics"), map them to the EXACT SAME resulting string (e.g. "Marketing_Data_Analysis_Exp").

[INPUT BATCH]
{batch}

[OUTPUT FORMAT]
You MUST return ONLY a raw JSON dictionary.
The keys MUST be the exact strings from the INPUT BATCH.
The values MUST be the cleaned, standardized, factual patterns following the rules above.
Do not output any markdown blocks like ```json.
"""

    batch_size = 10
    success_count = 0
    for i in range(0, len(missing_patterns), batch_size):
        batch = missing_patterns[i:i+batch_size]
        prompt = PROMPT_TEMPLATE.format(batch=json.dumps(batch, ensure_ascii=False))
        
        try:
            mapped = gemini.get_chat_completion_json(prompt)
            if mapped:
                current_mapping.update(mapped)
                success_count += len(mapped)
                print(f"  ✅ Mapped {len(mapped)} missing patterns.")
        except Exception as e:
            print(f"  ❌ Error on batch {i}: {e}")
            
        time.sleep(2)

    with open("pattern_mapping.json", "w", encoding="utf-8") as f:
        json.dump(current_mapping, f, ensure_ascii=False, indent=2)
        
    print(f"\nDone! Updated mapping now has {len(current_mapping)} patterns.")

if __name__ == "__main__":
    complete_mapping()
