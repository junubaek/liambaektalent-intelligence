import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    text = f.read()


injection = """    conds = extracted.get("conditions", [])
    def map_abbreviations_to_conds(query_str, conditions_list):
        expansion_map = {
            "IPO": ["Investor_Relations", "IPO_Preparation"],
            "IR": ["Investor_Relations"],
            "DFT": ["Design_for_Testability"],
            "RTL": ["RTL_Design"],
            "SoC": ["System_on_Chip"],
            "SAP": ["SAP_ERP"],
            "BI": ["Business_Intelligence"],
            "Tableau": ["Tableau"],
            "DevOps": ["DevOps", "CI_CD"],
            "SaaS": ["SaaS"],
            "Kotlin": ["Kotlin", "Android_Development"],
            "ASRS": ["Warehouse_Automation"]
        }
        import re
        for abbr, expansions in expansion_map.items():
            # Use regex to match abbreviation strictly
            if re.search(r'\\b' + re.escape(abbr) + r'\\b', query_str, re.IGNORECASE):
                for exp in expansions:
                    # check if already exists
                    if not any(c.get('skill') == exp for c in conditions_list):
                        conditions_list.append({"action": "MANAGED", "skill": exp, "is_mandatory": False, "source": "abbreviation_map"})
        return conditions_list

    conds = map_abbreviations_to_conds(prompt, conds)"""

if "conds = extracted.get(\"conditions\", [])" in text and "map_abbreviations_to_conds" not in text:
    text = text.replace("    conds = extracted.get(\"conditions\", [])", injection, 1)

with open(jd_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Abbreviation Map Injected.")
