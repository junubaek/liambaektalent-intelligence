
import json
import logging
from connectors.pinecone_api import PineconeClient
from connectors.openai_api import OpenAIClient
from connectors.gemini_api import GeminiClient
from jd_analyzer_v5 import JDAnalyzerV5
from classification_rules import get_role_cluster

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatcherV4_2:
    def __init__(self, secrets_path="secrets.json"):
        with open(secrets_path, "r") as f:
            self.secrets = json.load(f)
        
        pc_host = self.secrets.get("PINECONE_HOST", "")
        if not pc_host.startswith("https://"):
            pc_host = f"https://{pc_host}"
            
        self.pc = PineconeClient(self.secrets["PINECONE_API_KEY"], pc_host)
        self.openai = OpenAIClient(self.secrets["OPENAI_API_KEY"])
        self.gemini = GeminiClient(self.secrets["GEMINI_API_KEY"])
        self.analyzer = JDAnalyzerV5(self.openai)

    def analyze_jd(self, jd_text):
        logger.info("Analyzing JD (Minimal Thinking)...")
        return self.analyzer.analyze(jd_text)

    def search_candidates(self, jd_analysis, top_k=20):
        """
        [v6.0 Broad Pooling] 
        Recruits a wide set of candidates based on Category/Role alone 
        to ensure high recall before signal ranking.
        """
        logger.info(f"Broad searching candidates (Target: {top_k})...")
        
        # Build BROAD query string (Category centric)
        broad_role = jd_analysis.get('discovery_metadata', {}).get('broad_search_trigger', jd_analysis.get('canonical_role', ''))
        query_text = f"Professional Category: {broad_role}"
        logger.info(f"Broad Query: {query_text}")
        
        q_vec = self.openai.embed_content(query_text)
        if not q_vec:
            return []
            
        # Prepare Filter
        filter_meta = {}
        role_cluster = get_role_cluster(broad_role)
        if role_cluster != "기타":
            filter_meta["role_cluster"] = {"$eq": role_cluster}
            logger.info(f"Applying filter: {filter_meta}")
            
        # Try namespaces: v6.2-vs (enriched), ns1, default
        namespaces = ["v6.2-vs", "ns1", ""]
        matches = []
        
        for ns in namespaces:
            logger.info(f"Targeting namespace: {ns}")
            # Only apply cluster filter to non-empty namespaces if possible, 
            # or just try with filter and then without if 0 results
            res = self.pc.query(q_vec, top_k=top_k, filter_meta=filter_meta if filter_meta else None, namespace=ns)
            ms = res.get('matches', [])
            
            if not ms and filter_meta:
                logger.info(f"0 results with filter in {ns}. Retrying {ns} without filter...")
                res = self.pc.query(q_vec, top_k=top_k, namespace=ns)
                ms = res.get('matches', [])
                
            if ms:
                matches = ms
                logger.info(f"Found {len(matches)} matches in {ns}")
                break
        
        if not matches:
            logger.info("No matches found in any candidate namespace.")
            
        return matches

    def fetch_history(self, candidate_name):
        """Fetches history for a specific candidate from Pinecone."""
        # Query with metadata filter for exact name
        # We also use a small vector search (e.g. name embedding) as a fallback/primary
        q_vec = self.openai.embed_content(candidate_name)
        
        # Meta filter is more reliable for exact name
        filter_meta = {"name": {"$eq": candidate_name}}
        
        res = self.pc.query(q_vec, top_k=3, filter_meta=filter_meta, namespace="history_v4_2")
        matches = res.get('matches', [])
        
        history_entries = []
        for m in matches:
            history_entries.append(m['metadata'].get('history_note', ''))
            
        return " | ".join(history_entries) if history_entries else "No prior history found."

    def match_reasoning(self, jd_data, candidate_data, history_data):
        """
        [v6.0 Discovery Matcher]
        Focuses on literal signal alignment and Gap Analysis.
        """
        logger.info(f"Discovery-First reasoning for {candidate_data.get('name')}...")
        
        prompt = f"""
        [Role Context]
        - JD Role: {jd_data.get('canonical_role')}
        - Explicit Must-Haves: {jd_data.get('explicit_must_haves')}
        - Explicit Tools: {jd_data.get('explicit_tools')}
        - Inferred Metadata: {jd_data.get('discovery_metadata', {}).get('inferred_signals')}

        [Candidate Data]
        - Name: {candidate_data.get('name')}
        - Position: {candidate_data.get('position')}
        - Skills: {candidate_data.get('skill_set')}
        - Summary: {candidate_data.get('summary')}
        
        [Past History]
        - Signals: {history_data}

        [Matching Mission: v6.0 Gap-First]
        1. Literal Signal Check: Compare 'Explicit Must-Haves' and 'Tools' against candidate skills/summary literally.
        2. Gap Analysis: Identify EXPLICIT missing signals (e.g., JD asked for Tableau, but candidate only has Excel).
        3. Fact-Only Evidence: core_evidence must be a factual sentence mapping JD need to Candidate fact.
        4. Match Grade:
           - Perfect: Category + Explicit Tools/Behaviors ALL Match.
           - Strong: Category matches + Core Behaviors match (even if some tools differ).
           - Good: Category matches + Transferable skills identified.
           - Potential: Category matches + Gap analysis required.

        [Output Format]
        {{
          "match_grade": "Perfect | Strong | Good | Potential",
          "core_evidence": "Factual evidence string ([Job/Company/Result])",
          "gap_analysis": "Explicit Gap: 'Candidate lacks [Tool/Experience] mentioned in JD'",
          "matched_signals": ["Signal1", "Tool1"],
          "unmatched_signals": ["Signal2"]
        }}
        """
        
        result = self.gemini.get_chat_completion_json(prompt)
        return result

    def run_pipeline(self, jd_text):
        jd_analysis = self.analyze_jd(jd_text)
        candidates = self.search_candidates(jd_analysis)
        
        final_results = []
        for cand in candidates:
            meta = cand['metadata']
            name = meta.get('name', 'Unknown')
            
            history = self.fetch_history(name)
            match_json = self.match_reasoning(jd_analysis, meta, history)
            
            if match_json:
                res = {
                    "name": name,
                    "position": meta.get('position', 'Unknown'),
                    "seniority": meta.get('seniority_bucket') or meta.get('seniority') or meta.get('연차') or "UNKNOWN",
                    "match_grade": match_json.get('match_grade', 'Potential'),
                    "core_evidence": match_json.get('core_evidence', ''),
                    "gap_analysis": match_json.get('gap_analysis', ''),
                    "history_note": match_json.get('history_note', ''),
                    "matched_signals": match_json.get('matched_signals', []),
                    "unmatched_signals": match_json.get('unmatched_signals', []),
                    "summary": meta.get('experience_summary') or meta.get('resume_summary') or meta.get('summary', ''),
                    "mainSector": meta.get('main_sectors', ["기타"])[0] if isinstance(meta.get('main_sectors'), list) and meta.get('main_sectors') else "기타",
                    "experience_summary": meta.get('experience_summary', ''),
                    "resume_summary": meta.get('resume_summary', ''),
                    "skill_set": meta.get('skill_set', ''),
                    "sub_sectors": ", ".join(meta.get('sub_sectors', [])) if isinstance(meta.get('sub_sectors'), list) else (meta.get('sub_sectors') or ""),
                    "experience_patterns": ", ".join(meta.get('experience_patterns', [])) if isinstance(meta.get('experience_patterns'), list) else (meta.get('experience_patterns') or ""),
                    "notion_url": meta.get('url') or meta.get('notion_url', '#'),
                    "id": cand['id']
                }
                final_results.append(res)
                
        return final_results

if __name__ == "__main__":
    matcher = MatcherV4_2()
    test_jd = "핀테크 기업의 FP&A 매니저를 찾습니다. 예산 관리 및 경영 분석 경험 5년 이상 필수."
    results = matcher.run_pipeline(test_jd)
    print(json.dumps(results, indent=2, ensure_ascii=False))
