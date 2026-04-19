import json
import time
from notion_client import Client
from typing import Set

# Load the ontology mappings
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ontology_graph import CANONICAL_MAP
except ImportError:
    # Fallback if running from a different directory
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from ontology_graph import CANONICAL_MAP

import requests

# Setup Notion Client
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

NOTION_API_KEY = secrets["NOTION_API_KEY"]
DB_ID = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def extract_nodes_from_text(text: str) -> Set[str]:
    """
    텍스트 내에서 CANONICAL_MAP의 키워드를 스캔하여 
    정규화된 절대 노드 ID 세트를 반환합니다.
    """
    found_nodes = set()
    text_lower = text.lower()
    
    # 단순 매칭 (향후 정규식으로 단어 경계(Word boundary) 매칭 고도화 가능)
    for kw, node_id in CANONICAL_MAP.items():
        if kw.lower() in text_lower:
            found_nodes.add(node_id)
            
    return found_nodes

def fetch_and_sync():
    print("🚀 [Sync Bot] Starting Notion Graph Nodes Sync...")
    
    try:
        url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
        # 1페이지(100개)만 일단 테스트 동기화
        res = requests.post(url, headers=headers, timeout=15).json()
        if "results" not in res:
            print(f"❌ [에러] API 데이터 형식 오류: {res}")
            return
        pages = res.get("results", [])
    except Exception as e:
        print(f"❌ [에러] Notion API 호출 실패: {e}")
        return

    print(f"✅ 발견된 후보자 이력서: {len(pages)}건 (첫 페이지 기준)")

    updated_count = 0
    
    for page in pages:
        page_id = page["id"]
        props = page.get("properties", {})
        
        # 2. 텍스트 추출 (Functional Patterns 및 Experience Summary)
        # 만약 Functional Patterns가 multi_select에서 rich_text로 변경되었다면 rich_text로 읽습니다.
        # (기존 multi_select인 데이터도 대응하기 위해 예외 처리)
        combined_text = ""
        
        fp_prop = props.get("Functional Patterns", {})
        if fp_prop.get("type") == "rich_text":
            combined_text += " ".join([t["plain_text"] for t in fp_prop.get("rich_text", [])]) + " "
        elif fp_prop.get("type") == "multi_select":
            combined_text += " ".join([o["name"] for o in fp_prop.get("multi_select", [])]) + " "

        es_prop = props.get("Experience Summary", {})
        if es_prop.get("type") == "rich_text":
            combined_text += " ".join([t["plain_text"] for t in es_prop.get("rich_text", [])]) + " "

        ct_prop = props.get("Context Tags", {})
        if ct_prop.get("type") == "rich_text":
            combined_text += " ".join([t["plain_text"] for t in ct_prop.get("rich_text", [])]) + " "
            
        # 3. 매핑 및 추출
        if not combined_text.strip():
            continue
            
        detected_nodes = extract_nodes_from_text(combined_text)
        
        # 4. "[Graph_Nodes]" 필드가 존재하는지 확인 후 업데이트 (최대 100개 제한 준수)
        
        target_col = None
        for key in props.keys():
            if "Graph" in key or "Node" in key:
                target_col = key
                break
        
        if target_col is None:
            if updated_count == 0:
                print(f"⚠️ [디버깅] 현재 존재하는 컬럼들: {list(props.keys())}")
                return
            continue
            
        if detected_nodes:
            # Multi-select options
            multi_select_payload = [{"name": node} for node in list(detected_nodes)[:100]]
            
            try:
                # HTTP PATCH 요청으로 속성 업데이트
                update_url = f"https://api.notion.com/v1/pages/{page_id}"
                payload = {
                    "properties": {
                        target_col: {
                            "multi_select": multi_select_payload
                        }
                    }
                }
                
                resp = requests.patch(update_url, headers=headers, json=payload, timeout=15)
                if resp.status_code != 200:
                    print(f"⚠️ [업데이트 실패] API 응답 오류: {resp.text}")
                    continue
                
                # 이름 추출 (로깅용)
                name_prop = props.get("이름", {}).get("title", [])
                name = name_prop[0]["plain_text"] if name_prop else page_id
                
                print(f"🔄 [업데이트 완료] {name} -> {len(detected_nodes)}개의 노드 추출")
                updated_count += 1
                time.sleep(0.3) # Rate limit 방지
                
            except Exception as e:
                print(f"⚠️ [업데이트 실패] Page ID {page_id} - 상세: {e}")
                
    print(f"\n🎉 [Sync Bot] 동기화 종료! 총 {updated_count}건의 프로필이 Graph Node로 치환되었습니다.")

if __name__ == "__main__":
    fetch_and_sync()
