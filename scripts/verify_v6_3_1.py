import json
import sys
import os

# Add root to python path
sys.path.append(os.getcwd())

from headhunting_engine.jd_parser.jd_parser_v3 import JDParserV3
from connectors.gemini_api import GeminiClient # Or OpenAIClient
from connectors.notion_api import NotionClient

# Load Secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)

GEMINI_KEY = secrets["GEMINI_API_KEY"]
NOTION_TOKEN = secrets["NOTION_API_KEY"]
DISCOVERY_DB_ID = secrets["NOTION_DISCOVERY_DB_ID"]

def verify_discovery():
    print("🧪 Verifying JD Discovery Pipeline (v6.3.1)...")
    
    # 1. Sample JD with extreme emerging tech
    sample_jd = """
    [채용공고] Next-Gen AI Infrastructure Architect
    - 핵심 과제: Anthropic의 Model Context Protocol(MCP) 기반의 분산 에이전트 아키텍처 구축.
    - 기술 요건: LangGraph를 이용한 복합 에이전트 오케스트레이션 및 MCP 서버 구현 경험 필수.
    - 우대 사항: Agentic Workflow 최적화 및 신규 에이전트 표준 프로토콜 설계 유관 경험.
    """
    
    # 2. Parse JD
    client = GeminiClient(GEMINI_KEY)
    parser = JDParserV3(client, "headhunting_engine/universal_ontology.json")
    
    print("  [Step 1] Parsing JD for new signals...")
    result = parser.parse_jd(sample_jd)
    
    print(f"  [Result] Discovered Demands: {json.dumps(result.get('discovered_demands'), indent=2, ensure_ascii=False)}")
    
    # 3. Sync to Notion Discovery Hub
    if result.get('discovered_demands'):
        print("  [Step 2] Syncing to Notion Discovery Hub...")
        nc = NotionClient(NOTION_TOKEN)
        for demand in result.get('discovered_demands'):
            page = nc.create_discovery_page(
                DISCOVERY_DB_ID,
                demand.get('temp_name', 'Unnamed Trend'),
                "JD (수요)",
                result.get('primary_sector', 'TECH_SW'),
                demand.get('raw_text', ''),
                demand.get('market_scarcity_prediction', 'High')
            )
            if page:
                print(f"    ✅ Synced: {demand.get('temp_name')} -> {page.get('url')}")
    else:
        print("  ⚠️ No new demands discovered in this sample.")

if __name__ == "__main__":
    verify_discovery()
