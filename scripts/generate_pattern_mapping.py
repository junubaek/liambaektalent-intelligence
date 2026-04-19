import json
import time
import sys
import os

sys.path.append(os.getcwd())
from connectors.gemini_api import GeminiClient

def generate_mapping():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)

    gemini = GeminiClient(secrets["GEMINI_API_KEY"])

    with open("current_patterns.json", "r", encoding="utf-8") as f:
        all_patterns = json.load(f)

    print(f"Loaded {len(all_patterns)} patterns for mapping...")

    # We process in batches of 50 to avoid hitting output token limits or confusing the AI
    batch_size = 50
    final_mapping = {}

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

    for i in range(0, len(all_patterns), batch_size):
        batch = all_patterns[i:i+batch_size]
        print(f"Processing batch {i} to {i+len(batch)}...")
        
        prompt = PROMPT_TEMPLATE.format(batch=json.dumps(batch, ensure_ascii=False))
        
        # We rely on gemini_api.py fallback logic.
        try:
            mapped = gemini.get_chat_completion_json(prompt)
            if mapped:
                final_mapping.update(mapped)
                print(f"  ✅ Mapped {len(mapped)} patterns this batch.")
            else:
                print("  ⚠️ AI returned empty or failed to parse JSON for this batch.")
        except Exception as e:
            print(f"  ❌ Error on batch {i}: {e}")
            
        time.sleep(2) # Prevent rapid rate hitting

    # Save to file
    with open("pattern_mapping.json", "w", encoding="utf-8") as f:
        json.dump(final_mapping, f, ensure_ascii=False, indent=2)
        
    print(f"\nDone! Generated mapping for {len(final_mapping)} patterns.")

if __name__ == "__main__":
    generate_mapping()
