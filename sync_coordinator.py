
import json
import logging
import os
import time
from datetime import datetime, timezone
from connectors.notion_api import HeadhunterDB, NotionClient
from connectors.pinecone_api import PineconeClient
from connectors.openai_api import OpenAIClient
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STATUS_FILE = "sync_status.json"
NAMESPACE = "v6.2-vs"

class SyncCoordinator:
    def __init__(self, secrets_path="secrets.json"):
        with open(secrets_path, "r") as f:
            self.secrets = json.load(f)
            
        self.notion_db = HeadhunterDB(secrets_path)
        self.notion_client = self.notion_db.client
        
        pc_host = self.secrets.get("PINECONE_HOST", "")
        if not pc_host.startswith("https://"): pc_host = f"https://{pc_host}"
        
        self.pinecone = PineconeClient(self.secrets["PINECONE_API_KEY"], pc_host)
        self.openai = OpenAIClient(self.secrets["OPENAI_API_KEY"])
        
    def get_last_sync_time(self):
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_sync_time")
        return None

    def save_last_sync_time(self, timestamp):
        with open(STATUS_FILE, "w") as f:
            json.dump({"last_sync_time": timestamp}, f)

    def get_ascii_id(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:32]

    def build_semantic_profile(self, cand_props):
        """Constructs text for embedding from Notion properties."""
        name = cand_props.get('이름') or cand_props.get('name') or "Unknown"
        sectors = cand_props.get('main_sectors', [])
        sub_sectors = cand_props.get('sub_sectors', [])
        summary = cand_props.get('experience_summary', '')
        
        profile = f"Candidate: {name}\n"
        profile += f"Sectors: {', '.join(sectors)}\n"
        profile += f"Sub Sectors: {', '.join(sub_sectors)}\n"
        profile += f"Summary: {summary}"
        return profile

    def sync_recent_changes(self, limit=100):
        last_sync = self.get_last_sync_time()
        logger.info(f"Checking for changes since {last_sync if last_sync else 'Beginning'}...")
        
        # 1. Query Notion for pages edited after last_sync
        filter_criteria = None
        if last_sync:
            filter_criteria = {
                "timestamp": "last_edited_time",
                "last_edited_time": {
                    "after": last_sync
                }
            }
            
        db_id = self.secrets.get("NOTION_DATABASE_ID")
        if not db_id:
            logger.error("NOTION_DATABASE_ID not found in secrets.json")
            return 0
            
        res = self.notion_client.query_database(db_id, limit=limit, filter_criteria=filter_criteria)
        pages = res.get('results', [])
        
        if not pages:
            logger.info("No changes detected.")
            return 0
            
        logger.info(f"Detected {len(pages)} changed records. Upserting to Pinecone...")
        
        vectors = []
        for page in pages:
            # Re-fetch candidate details to get full properties properly extracted
            cand_props = self.notion_client.extract_properties(page)
            name = cand_props.get('이름') or cand_props.get('name') or "Unknown"
            
            profile_text = self.build_semantic_profile(cand_props)
            embedding = self.openai.embed_content(profile_text)
            
            if not embedding:
                continue
                
            metadata = {
                "name": name,
                "position": cand_props.get('포지션') or cand_props.get('position') or 'Unclassified',
                "skill_set": ", ".join(cand_props.get('sub_sectors', [])), 
                "summary": profile_text[:800],
                "role_cluster": cand_props.get('role_cluster', '기타'),
                "url": cand_props.get('url') or "",
                "main_sectors": cand_props.get('main_sectors', []),
                "sub_sectors": cand_props.get('sub_sectors', []),
                "experience_patterns": cand_props.get('experience_patterns', []),
                "experience_summary": cand_props.get('experience_summary', ""),
                "resume_summary": cand_props.get('resume_summary', "")
            }
            
            vectors.append({
                "id": self.get_ascii_id(name),
                "values": embedding,
                "metadata": metadata
            })
            
        if vectors:
            # Upsert in batches of 100 to avoid size limits
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.pinecone.upsert(batch, namespace=NAMESPACE)
                logger.info(f"Successfully synced batch {i//batch_size + 1} ({len(batch)} records).")
            
            # Update last sync time to NOW
            now_str = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            self.save_last_sync_time(now_str)
            
        return len(vectors)

if __name__ == "__main__":
    coordinator = SyncCoordinator()
    coordinator.sync_recent_changes(limit=20)
