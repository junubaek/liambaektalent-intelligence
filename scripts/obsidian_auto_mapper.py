import os
import json
import logging
import re
from app.graph_engine.obsidian_parser import ObsidianParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AutoMapper")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES_JSON = os.path.join(ROOT_DIR, "temp_500_candidates.json")
VAULT_DIR = os.path.join(ROOT_DIR, "obsidian_vault")
CANONICAL_FILE = os.path.join(VAULT_DIR, "Meta", "canonical_map.yaml")
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")

def load_secrets():
    with open(SECRETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_unmapped_keywords():
    logger.info("Parsing Obsidian Graph...")
    parser = ObsidianParser(VAULT_DIR)
    parsed_nodes = parser.parse_all_nodes()
    
    # 1. 기존 매핑된 Alias 수집
    alias_map = {}
    for node in parsed_nodes:
        n_id = node.get("id")
        for al in node.get("aliases", []):
            # 띄어쓰기 제거 및 축소해서 매칭률 높이기
            clean_al = al.replace(" ", "").lower()
            alias_map[clean_al] = n_id
            
    # 2. Notion JSON 파싱 (Sub Sectors, Functional Patterns)
    logger.info(f"Reading Notion Dump: {CANDIDATES_JSON}")
    if not os.path.exists(CANDIDATES_JSON):
        logger.error(f"Cannot find {CANDIDATES_JSON}")
        return [], []
        
    with open(CANDIDATES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    results = data.get('results', [])
    all_raw_tags = set()
    
    for c in results:
        props = c.get('properties', {})
        for prop_name, prop_data in props.items():
            prop_type = prop_data.get('type')
            
            # Extract tags
            if any(k in prop_name.lower() for k in ['functional patterns', 'sub sectors']):
                if prop_type == 'multi_select':
                    all_raw_tags.update([item['name'] for item in prop_data.get('multi_select', [])])
                elif prop_type == 'rich_text':
                    text_content = "".join([t.get('plain_text', '') for t in prop_data.get('rich_text', [])])
                    if ',' in text_content:
                        all_raw_tags.update([x.strip() for x in text_content.split(',') if x.strip()])
                        
    # 3. Diff 추출
    unmapped = set()
    for tag in all_raw_tags:
        cleaned = tag.strip().replace("\n", "")
        if not cleaned or len(cleaned) < 2:
            continue
            
        clean_tag = cleaned.replace(" ", "").lower()
        if clean_tag not in alias_map:
            # Check partial overlap logically, but for strictness just add to unmapped
            unmapped.add(cleaned)
            
    existing_nodes = list(set(alias_map.values()))
    return list(unmapped), existing_nodes, alias_map

def map_with_gemini(unmapped_keywords, existing_nodes, api_key):
    if not unmapped_keywords:
        return {}
        
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    # gemini-2.5-flash is extremely fast and accurate
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    batch_size = 50
    new_mappings = {}
    
    # Existing nodes list in prompt
    nodes_str = "\n".join([f"- {n}" for n in existing_nodes])
    
    for i in range(0, len(unmapped_keywords), batch_size):
        batch = unmapped_keywords[i:i+batch_size]
        logger.info(f"Gemini processing batch {i//batch_size + 1}/{(len(unmapped_keywords)//batch_size)+1} (size: {len(batch)})...")
        
        prompt = f"""
You are the Chief AI Taxonomy Architect for a Headhunting OS.
We are mapping wild, unstructured resume keywords (Functional Patterns) rigidly into our Pre-defined Master Ontology Nodes.

[EXISTING MASTER NODES (DO NOT CREATE NEW ONES)]
{nodes_str}
- 기타 (Others)

[WILD KEYWORDS TO MAP]
{json.dumps(batch, ensure_ascii=False)}

[TASK]
For each wild keyword, find the ABSOLUTE CLOSEST conceptual Master Node.
- Example 1: If keyword is "IPO 경험", map to "자금" or "재무회계"
- Example 2: If keyword is "Kubernetes", map to "인프라_Cloud"
- Example 3: If keyword is "투자유치", map to "IR" or "투자담당자"
- Output "기타" ONLY if it's completely irrelevant or non-professional jargon.

[OUTPUT FORMAT (STRICT JSON WITHOUT MARKDOWN)]
{{"mappings": [{{"keyword": "str", "mapped_node": "str"}}]}}
        """
        
        try:
            response = model.generate_content(prompt, generation_config={"temperature": 0.1})
            raw = re.sub(r"```json|```", "", response.text.strip()).strip()
            
            res_json = json.loads(raw)
            for mapping in res_json.get("mappings", []):
                node = mapping.get("mapped_node", "")
                kw = mapping.get("keyword", "")
                if node in existing_nodes and node != "기타":
                    new_mappings[kw] = node
        except Exception as e:
            logger.error(f"Gemini API / Parsing failure on batch {i}: {e}")
            logger.error(f"Raw Output: {response.text if 'response' in locals() else 'None'}")
            
    return new_mappings

def append_to_canonical(new_mappings):
    if not new_mappings:
        logger.info("No newly mapped aliases to append.")
        return
        
    with open(CANONICAL_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n# Auto-Mapped by Phase 10 Discovery Pipeline\n")
        count = 0
        for kw, node in new_mappings.items():
            if ":" not in kw and len(kw) > 1: # Sanity check for valid YAML keys
                f.write(f"{kw}: {node}\n")
                count += 1
            
    logger.info(f"✨ Successfully appended {count} new terms to canonical_map.yaml")

if __name__ == "__main__":
    logger.info("Starting Obsidian Context Auto-Mapper...")
    secrets = load_secrets()
    
    unmapped, nodes, current_aliases = build_unmapped_keywords()
    logger.info(f"Total Master Nodes: {len(nodes)}")
    logger.info(f"Total Unique Aliases currently mapped: {len(current_aliases)}")
    logger.info(f"Found {len(unmapped)} completely unmapped wild keywords in Notion.")
    
    if len(unmapped) > 0:
        logger.info(f"Sample unmapped: {unmapped[:10]}")
        mappings = map_with_gemini(unmapped, nodes, secrets["GEMINI_API_KEY"])
        logger.info(f"Gemini successfully mapped {len(mappings)} keywords.")
        append_to_canonical(mappings)
    else:
        logger.info("Vault is completely synced. No unmapped tags found.")
