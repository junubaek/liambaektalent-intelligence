import json
import argparse
import os
import sys

# Define base project path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.pinecone_api import PineconeClient
from connectors.gemini_api import GeminiClient
from connectors.openai_api import OpenAIClient
from jd_confidence import estimate_jd_confidence
from search_strategy import decide_search_strategy
from classification_rules import get_role_cluster
from jd_analyzer_v8 import JDAnalyzerV8

# --- [v8.0] SCORING WEIGHTS ---
WEIGHTS = {
    "VECTOR_RELEVANCE": 0.40,  # Semantic Match
    "FUNCTIONAL_PATTERN": 0.30, # Rule 1/Gate 3 (Verb + Object)
    "CONTEXT_TAG_BONUS": 0.15,  # Rule 2 (Niche Tech tags)
    "QUANT_TIER": 0.10,
    "QUANT_EXP": 0.05
}

def calculate_final_score_v8(vector_score, metadata, target_patterns, target_tags):
    """
    [v8.0] Enhanced scoring with Reciprocal Dynamic Tagging awareness.
    """
    # 1. Pattern Match Calculation (Verb + Object)
    candidate_patterns = metadata.get('experience_patterns', [])
    if isinstance(candidate_patterns, str):
        try:
            candidate_patterns = json.loads(candidate_patterns)
        except:
            candidate_patterns = []
            
    pattern_match_count = 0
    if target_patterns and candidate_patterns:
        # We look for partial string matches for robustness
        t_set = set([p.lower() for p in target_patterns])
        c_set = set([p.lower() for p in candidate_patterns])
        matches = t_set.intersection(c_set)
        pattern_match_count = len(matches)
        
    norm_pattern = min(1.0, pattern_match_count / 3.0) if target_patterns else 0.5
    
    # 2. Context Tag Bonus (Niche requirements)
    tag_match_count = 0
    candidate_skills = metadata.get('skills', []) # Fallback to general skills if tags not split
    if target_tags and candidate_skills:
        t_tags = set([t.lower() for t in target_tags])
        c_skills = set([s.lower() for s in candidate_skills])
        tag_match_count = len(t_tags.intersection(c_skills))
    
    norm_tags = min(1.0, tag_match_count / 2.0) if target_tags else 0.0
    
    # 3. Traditional Multipliers
    tier_score = float(metadata.get('company_tier_score', 0))
    norm_tier = min(1.0, tier_score / 10.0)
    
    # 4. Weighted Sum
    final_score = (
        (vector_score * WEIGHTS["VECTOR_RELEVANCE"]) +
        (norm_pattern * WEIGHTS["FUNCTIONAL_PATTERN"]) +
        (norm_tags * WEIGHTS["CONTEXT_TAG_BONUS"]) +
        (norm_tier * WEIGHTS["QUANT_TIER"])
    )
    
    return final_score * 100

def deduplicate_results(results_list):
    seen = {}
    final_list = []
    for batch in results_list:
        for match in batch:
            mid = match['id']
            if mid not in seen:
                seen[mid] = match
                final_list.append(match)
            elif match['score'] > seen[mid]['score']:
                seen[mid] = match
                for i, item in enumerate(final_list):
                    if item['id'] == mid:
                        final_list[i] = match
                        break
    return final_list

def search_candidates(jd_text, limit=5):
    # 1. Load Secrets
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
        
    pc_host = secrets.get("PINECONE_HOST", "")
    if pc_host and not pc_host.startswith("https://"):
        pc_host = f"https://{pc_host}"

    pinecone = PineconeClient(secrets["PINECONE_API_KEY"], pc_host)
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    analyzer = JDAnalyzerV8(gemini)
    
    print(f"🚀 [v8.0] Analyzing JD with Gemini 3.0 Flash...")
    semantic_data = analyzer.analyze(jd_text)
    
    target_patterns = semantic_data.get("functional_patterns", [])
    target_tags = semantic_data.get("context_tags", [])
    main_sectors = semantic_data.get("main_sectors", [])
    sub_sectors = semantic_data.get("sub_sectors", [])
    
    print(f"  -> Sectors: {', '.join(main_sectors)} | {', '.join(sub_sectors)}")
    print(f"  -> Targeted Patterns: {target_patterns}")
    print(f"  -> Context Tags: {target_tags}")
    
    # 2. Strategy & Confidence
    confidence_score = estimate_jd_confidence({
        "explicit_skills": target_tags,
        "title_candidates": main_sectors + sub_sectors,
        "domain_clues": target_patterns,
        "seniority_clues": [str(semantic_data.get('seniority', {}).get('min_years', 0))]
    })
    strategy = decide_search_strategy(confidence_score)
    
    # 3. Ensemble Search (Note: Using OpenAI for 1536-dim compatibility with existing index)
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    semantic_query = f"Sectors: {', '.join(main_sectors)} | {', '.join(sub_sectors)} / Patterns: {', '.join(target_patterns)} / Tags: {', '.join(target_tags)}"
    print(f"  -> Generating Embeddings (OpenAI 1536-dim)...")
    q_vec = openai.embed_content(semantic_query)
    
    filter_meta = {}
    min_years = semantic_data.get('seniority', {}).get('min_years', 0)
    if min_years > 0:
        filter_meta['total_years'] = {"$gte": min_years}
    
    # v8.0 Sector filter logic: Allow broader matching if cluster is known
    # if role_cluster != "Unclassified":
    #     filter_meta['primary_sector'] = {"$eq": primary_sector}

    print(f"  -> Querying Pinecone v8 (Top-K: {strategy['top_k']})")
    res = pinecone.query(q_vec, top_k=strategy['top_k'], filter_meta=filter_meta)
    
    if not res or 'matches' not in res:
        print("❌ No matches found in Pinecone.")
        return []

    # 4. Hybrid Ranking v8.0
    ranked_candidates = []
    for match in res['matches']:
        vec_score = match['score']
        meta = match['metadata']
        
        final_score = calculate_final_score_v8(vec_score, meta, target_patterns, target_tags)
        
        ranked_candidates.append({
            "name": meta.get('name', 'Unknown'),
            "final_score": final_score,
            "vector_score": vec_score,
            "matched_tags": list(set([t.lower() for t in target_tags]).intersection(set([s.lower() for s in meta.get('skills', [])]))),
            "summary": f"{meta.get('position', '')} at {meta.get('current_company', '')}",
            "id": match['id']
        })

    ranked_candidates.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Output
    print(f"\n{'RANK':<5} | {'SCORE':<6} | {'NAME':<20} | {'MATCHED TAGS':<30}")
    print("-" * 85)
    for i, cand in enumerate(ranked_candidates[:limit]):
        tags_str = ", ".join(cand['matched_tags']) if cand['matched_tags'] else "None"
        print(f"{i+1:<5} | {cand['final_score']:<.1f}   | {cand['name']:<20} | {tags_str[:30]}")
        
    return ranked_candidates

if __name__ == "__main__":
    test_jd = """
    We need a Senior Semiconductor Design Engineer with expertise in SoC Architecture 
    and HBM3 interface design. 10+ years experience.
    """
    search_candidates(test_jd)
