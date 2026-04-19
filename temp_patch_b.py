import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Clean up my Option 1 patch if it exists
if "# [Option 1 Patch]" in text:
    lines = text.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if line.strip() == "# [Option 1 Patch] 약어 확장 로직":
            skip = True
        if skip and line.strip() == "logging.getLogger(__name__).error(f\"[LLM Expansion Failed] {e}\")":
            skip = False
            continue
        if skip and line.strip() == "jd_text = _expanded":
            continue
        if not skip:
            # Need to also skip the except Exception block
            pass
            
    # Actually, regex is safer to remove it completely
    text = re.sub(r"[ \t]*# \[Option 1 Patch\].*?except Exception as e:.*?\[LLM Expansion Failed\].*?\"\)[\n\r]+", "", text, flags=re.DOTALL)


# 2. Update Depth Multiplier 1.6 -> 1.3
text = re.sub(
    r"DEPTH_MULTIPLIER\s*=\s*\{1:\s*1\.0,\s*2:\s*1\.3,\s*3:\s*1\.5,\s*4:\s*1\.6\}",
    "DEPTH_MULTIPLIER = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3}",
    text
)

# 3. Update Synergy / ACTION_WEIGHTS
# Based on the user's perception of "Synergy Multiplier: 1.8 -> 1.4"
# The most explicit reference to 1.8 in jd_compiler is `CLOSED` and `LED`. Let's replace those from 1.8 to 1.4.
text = re.sub(r"'CLOSED':\s*1\.8,", "'CLOSED': 1.4,", text)
text = re.sub(r"'LED':\s*1\.8,", "'LED': 1.4,", text)

# Also let's set it in inject_node_affinity just in case it was meant for that
if "weight * (1.4 / 1.8)" not in text:
    text = text.replace(
        '"weight": weight,',
        '"weight": weight * (1.4 / 1.8), # Synergy Multiplier applied'
    )


# 4. Insert expand_query_abbreviations in api_search_v8
target = """    emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding"""

replacement = """    def expand_query_abbreviations(query: str) -> str:
        expansion_map = {
            "IPO": "IPO 기업공개 상장준비 공모",
            "IR": "IR 투자자관계 Investor_Relations",
            "DFT": "DFT Design_for_Testability",
            "RTL": "RTL RTL_Design Register_Transfer_Level",
            "SoC": "SoC System_on_Chip 시스템반도체",
            "SAP": "SAP ERP SAP_ERP",
            "BI": "BI Business_Intelligence 데이터시각화",
            "Tableau": "Tableau Data_Visualization BI_Dashboard",
            "DevOps": "DevOps CI_CD 개발운영",
            "SaaS": "SaaS 클라우드서비스",
            "Kotlin": "Kotlin Android_Development",
            "DFE": "DFE Decision_Feedback_Equalizer",
            "ASRS": "ASRS 자동창고 자동화물보관",
        }
        import re
        expanded = query
        for abbr, expansion in expansion_map.items():
            # Use regex with word boundaries internally but just replace if needed
            expanded = expanded.replace(abbr, expansion)
        return expanded

    embedding_query = expand_query_abbreviations(prompt)
    logger.info(f"Expanded Embedding Query: {embedding_query}")
    
    emb_res = client.embeddings.create(input=[embedding_query], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding"""

if target in text:
    text = text.replace(target, replacement)
else:
    print("WARNING: Could not find target embedding logic in api_search_v8!! Trying regex...")
    # fallback regex
    target2 = r"emb_res = client\.embeddings\.create\(input=\[prompt\], model=\"text-embedding-3-small\"\)\s*query_vector = emb_res\.data\[0\]\.embedding"
    text = re.sub(target2, replacement, text)

with open(jd_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Patching complete.")

