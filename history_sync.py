
import json
import logging
from connectors.notion_api import NotionClient, HeadhunterDB
from connectors.pinecone_api import PineconeClient
from connectors.openai_api import OpenAIClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sync_history():
    # 1. Load Secrets
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    notion = NotionClient(secrets["NOTION_API_KEY"])
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    
    pc_host = secrets.get("PINECONE_HOST", "")
    if not pc_host.startswith("https://"):
        pc_host = f"https://{pc_host}"
    pc = PineconeClient(secrets["PINECONE_API_KEY"], pc_host)
    
    program_db_id = "756285ea-c39e-4315-8530-8e4154488d03"
    master_db_id = secrets["NOTION_DATABASE_ID"] # 🌌 AI Talent Intelligence v8.0 Master Hub
    
    logger.info(f"Fetching history from PROGRAM DB...")
    res = notion.query_database(program_db_id)
    pages = res.get('results', [])
    logger.info(f"Found {len(pages)} history records.")
    
    history_vectors = []
    
    for page in pages:
        props = notion.extract_properties(page)
        
        name = props.get('후보자', 'Unknown')
        status = props.get('전형', 'None')
        drop_reason = props.get('드랍사유', 'None')
        
        # 2. Map Signal
        signal_type = "Neutral"
        is_positive = False
        
        if status in ["면접탈락", "최종합격", "면접합격", "서류합격"]:
            signal_type = "Positive"
            is_positive = True
        elif status == "서류탈락":
            if drop_reason == "미스매치":
                signal_type = "Negative_Strong"
            elif drop_reason == "역량부족":
                signal_type = "Negative_Weak"
            else:
                signal_type = "Negative_Unknown"
        elif status in ["처우", "마감", "알수없음"]:
            signal_type = "Neutral"
            
        if signal_type == "Neutral":
            continue # Skip neutrals to save vector space if needed, or keep for context
            
        # 3. Build Description
        # We need JD context. Let's try to fetch the PROJECT info if related
        project_relation = props.get('project', []) # Relation property
        project_context = "Unknown Project"
        if project_relation and isinstance(project_relation, list):
            # Fetch first related project title
            try:
                proj_page = notion.get_page(project_relation[0]['id'] if isinstance(project_relation[0], dict) else project_relation[0])
                proj_props = notion.extract_properties(proj_page)
                project_context = proj_props.get('이름', 'Unknown Project')
            except:
                pass
        
        # History Note Format
        history_note = f"[{'긍정' if is_positive else '역신호'}] {status}: [결과] {status}({signal_type}) [프로젝트] {project_context} [후보자] {name}"
        
        # 4. Embed
        logger.info(f"Embedding history for {name}: {status}")
        vec = openai.embed_content(history_note)
        
        if vec:
            # Match Pinecone's index dimension (1536 as per error message)
            history_vectors.append({
                "id": f"hist_{page['id']}",
                "values": vec,
                "metadata": {
                    "name": str(name or ""),
                    "status": str(status or ""),
                    "drop_reason": str(drop_reason or "N/A"),
                    "signal_type": str(signal_type or ""),
                    "project": str(project_context or ""),
                    "history_note": str(history_note or ""),
                    "type": "history"
                }
            })
            
    # 5. Upsert to Pinecone
    if history_vectors:
        logger.info(f"Upserting {len(history_vectors)} history vectors to namespace: history_v4_2")
        # Upsert in batches of 100
        for i in range(0, len(history_vectors), 100):
            batch = history_vectors[i:i+100]
            pc.upsert(batch, namespace="history_v4_2")
        logger.info("History sync complete.")
    else:
        logger.warning("No valid history records found to sync.")

if __name__ == "__main__":
    sync_history()
