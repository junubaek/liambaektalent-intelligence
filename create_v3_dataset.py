import json
import sys
sys.stdout.reconfigure(line_buffering=True)
import requests
import time
import google.generativeai as genai

def get_notion_pages(api_key, db_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    pages = []
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    has_more = True
    next_cursor = None
    
    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        pages.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
        
    # Map title to page ID
    title_to_id = {}
    for p in pages:
        props = p.get("properties", {})
        # Find which property is the title
        for k, v in props.items():
            if v.get("type") == "title":
                title_arr = v.get("title", [])
                if title_arr:
                    title = title_arr[0].get("plain_text", "").strip()
                    title_to_id[title] = p["id"]
                    
    return title_to_id, headers

def get_page_blocks_text(page_id, headers):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = requests.get(url, headers=headers)
    blocks = res.json().get("results", [])
    
    full_text = []
    for b in blocks:
        b_type = b.get("type")
        if b_type and b_type in b:
            rich_text = b[b_type].get("rich_text", [])
            for rt in rich_text:
                full_text.append(rt.get("plain_text", ""))
    return "\n".join(full_text)[:2000] # limiting to first 2000 chars for LLM to avoid giant prompts

def extract_skills(model, jd_title, jd_text):
    prompt = f"""
다음은 '{jd_title}' 포지션의 실제 채용 공고(JD) 본문입니다.
이 포지션에서 가장 핵심적으로 요구하는 기술 스택 또는 스킬 키워드를 2~3개만 영문으로 추출하세요.
일반적인 '커뮤니케이션 능력' 말고 반드시 '구체적인 딥테크/하드스킬 키워드' (예: vLLM, PyTorch, Kubernetes, treasury 등)를 추출해야 합니다.
결과는 불필요한 서술 없이 기술 키워드들을 띄어쓰기로 구분해서 딱 1줄로만 출력하세요.

JD 본문:
{jd_text}
"""
    for _ in range(3):
        try:
            res = model.generate_content(prompt)
            txt = res.text.strip().replace("\n", " ").replace(",", " ")
            # limit output to safe keyword string
            return txt
        except Exception as e:
            time.sleep(3)
    return jd_title # fallback to original

def main():
    print("🚀 V3 Golden Dataset 생성 시작...")
    
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    try:
        genai.configure(api_key=secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash-8b")
        model.generate_content("test")
    except:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
    PROJECT_DB_ID = "1ef4807f-4b58-4fec-ab66-5c2e593b1ca4"
    print("1️⃣ Notion PROJECT DB 인덱싱 중...")
    title_to_id, headers = get_notion_pages(secrets["NOTION_API_KEY"], PROJECT_DB_ID)
    print(f"   => 총 {len(title_to_id)}개의 페이지 발견.")
    
    print("2️⃣ golden_dataset.json 쿼리 교체 중...")
    with open("golden_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    unique_queries = set(d["jd_query"] for d in dataset)
    print(f"   => 고유 직무명(jd_query) 개수: {len(unique_queries)}건")
    
    query_mapping = {}
    processed = 0
    
    for q in unique_queries:
        processed += 1
        print(f"      [{processed}/{len(unique_queries)}] '{q}' 처리 중...")
        
        # 1. Match with notion title
        matched_id = title_to_id.get(q)
        if not matched_id:
            # Fuzzy match?
            for title in title_to_id.keys():
                if q.lower() in title.lower() or title.lower() in q.lower():
                    matched_id = title_to_id[title]
                    break
                    
        if matched_id:
            # 2. Fetch Text
            jd_text = get_page_blocks_text(matched_id, headers)
            # 3. LLM AI Extraction
            skills = extract_skills(model, q, jd_text)
            query_mapping[q] = skills
            print(f"         > AI 추출 완료: {skills}")
        else:
            # If completely not found in Notion, just use LLM to infer from title
            skills = extract_skills(model, q, "없음")
            query_mapping[q] = skills
            print(f"         > Notion JDs Not Found. Title Infer: {skills}")
            
    print("3️⃣ golden_dataset_v3.json 저장 중...")
    for item in dataset:
        old_q = item["jd_query"]
        new_q = query_mapping.get(old_q, old_q)
        item["jd_query"] = new_q
        
    with open("golden_dataset_v3.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 완료! (총 {len(dataset)}건 항목 업데이트됨)")

if __name__ == "__main__":
    main()
