import os
import json
import logging
import sys
import difflib

# Add project root to path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

def orchestrate_powershell_backfill():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    db = HeadhunterDB(secrets_path)
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(gemini)
    
    with open("commands.ps1", "w", encoding="utf-8") as ps1:
        ps1.write(f"$Headers = @{{ 'Authorization' = 'Bearer {secrets['NOTION_API_KEY']}'; 'Notion-Version' = '2022-06-28'; 'Content-Type' = 'application/json' }}\n\n")
        
        # 1. Fetch Schema & Missing via pure PS
        ps1.write("Write-Host '1. Fetching Schema...'\n")
        ps1.write(f"$schema = Invoke-RestMethod -Uri 'https://api.notion.com/v1/databases/{secrets['NOTION_DATABASE_ID']}' -Headers $Headers -Method GET\n")
        ps1.write("$schema | ConvertTo-Json -Depth 10 | Out-File -FilePath temp_schema.json -Encoding utf8\n\n")
        
        ps1.write("Write-Host '2. Fetching Candidates...'\n")
        filter_payload = json.dumps({"filter": {"property": "Functional Patterns", "multi_select": {"is_empty": True}}, "page_size": 100})
        ps1.write(f"$q_payload = '{filter_payload}'\n")
        ps1.write(f"$cands = Invoke-RestMethod -Uri 'https://api.notion.com/v1/databases/{secrets['NOTION_DATABASE_ID']}/query' -Headers $Headers -Method POST -Body $q_payload\n")
        ps1.write("$cands | ConvertTo-Json -Depth 10 | Out-File -FilePath temp_candidates.json -Encoding utf8\n\n")

    print("[Python] Generated commands.ps1 to fetch data.")

def parse_and_generate_uploads():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    db = HeadhunterDB(secrets_path)
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(gemini)
    
    # Read temp_schema and temp_candidates
    try:
        with open("temp_schema.json", "r", encoding="utf-8-sig") as f:
            schema_data = json.load(f)
        with open("temp_candidates.json", "r", encoding="utf-8-sig") as f:
            cand_data = json.load(f)
    except FileNotFoundError:
        print("Data files missing. Run PS script first.")
        return
        
    options = schema_data["properties"]["Functional Patterns"].get("multi_select", {}).get("options", []) if "properties" in schema_data else []
    existing_patterns = [opt["name"] for opt in options]
    print(f"Loaded {len(existing_patterns)} schema options.")
    
    # Get already processed candidates to allow resuming
    processed_ids = set()
    if os.path.exists("uploads2.ps1"):
        with open("uploads2.ps1", "r", encoding="utf-8") as out:
            content = out.read()
            # Extract IDs from the API URLs in the existing file
            import re
            ids = re.findall(r"pages/([a-zA-Z0-9\-]+)'", content)
            processed_ids = set(ids)
            print(f"Found {len(processed_ids)} already processed candidates. Resuming...")
            
    # Open in append mode if it exists, otherwise write mode with header
    mode = "a" if os.path.exists("uploads2.ps1") else "w"
    
    with open("uploads2.ps1", mode, encoding="utf-8") as out:
        if mode == "w":
            head = f"$Headers = @{{ 'Authorization' = 'Bearer {secrets['NOTION_API_KEY'].strip()}'; 'Notion-Version' = '2022-06-28' }}\n\n"
            out.write(head)
            out.write("$ErrorActionPreference = 'Stop'\n\n")
        
        pages = cand_data.get("results", [])
        print(f"Processing {len(pages)} candidates...")
        
        for i, p in enumerate(pages):
            cand_id = p["id"]
            if cand_id in processed_ids:
                continue
                
            props = p.get("properties", {})
            name_prop = props.get("Name", {}).get("title", [])
            name = name_prop[0]["plain_text"] if name_prop else str(cand_id)
            
            full_text = ""
            summary_arr = props.get("Experience_Summary", {}).get("rich_text", [])
            full_text = "".join([t.get("plain_text", "") for t in summary_arr]) if summary_arr else ""
            
            if not full_text: 
                role = props.get("Role", {}).get("rich_text", [])
                role_val = "".join([t.get("plain_text", "") for t in role]) if role else ""
                
                sector_multi = props.get("Sub Sectors", {}).get("multi_select", [])
                sector_val = " ".join([s.get("name", "") for s in sector_multi]) if sector_multi else ""
                
                full_text = f"{role_val} {sector_val}".strip()
                 
            if not full_text: 
                print(f"[{i}] Skipping {name}: No full text or role found.")
                continue
                 
            # Add retry logic for Gemini parsing
            parsed = {}
            for attempt in range(4):
                try:
                    parsed = parser.parse(full_text)
                    if parsed: break
                except Exception as e:
                    import time
                    err_str = str(e)
                    if "429" in err_str or "Too Many Requests" in err_str:
                        print(f"Rate limit exceeded for {name}. Sleeping for 30s... (Attempt {attempt+1}/4)")
                        time.sleep(30)
                    else:
                        print(f"Attempt {attempt+1} failed for {name}: {e}")
                        time.sleep(2)
            
            patterns = parsed.get("patterns", []) if isinstance(parsed, dict) else []
            safe_pt = set()
            
            for pt in patterns:
                raw_pt = pt.get("verb_object", "").strip().replace(",", " ")
                if raw_pt:
                    if len(existing_patterns) >= 90:
                        matches = difflib.get_close_matches(raw_pt, existing_patterns, n=1, cutoff=0.3)
                        final_pt = matches[0] if matches else (existing_patterns[0] if existing_patterns else raw_pt)
                    else:
                        final_pt = raw_pt
                        
                    safe_pt.add(final_pt[:100])
                    if final_pt not in existing_patterns:
                        existing_patterns.append(final_pt)
                        
            if not safe_pt:
                print(f"[{i}] Gemini couldn't map {name}. Applying fallback.")
                fallback = "General Professional Experience"
                if fallback not in existing_patterns: existing_patterns.append(fallback)
                safe_pt.add(fallback)

            if safe_pt:
                out.write(f"Write-Host 'Updating {name}'\n")
                ps_tags = ", ".join([f"@{{ name = '{s.replace(chr(39), chr(39)*2)}' }}" for s in list(safe_pt)[:20]])
                
                out.write(f"$p = @{{ properties = @{{ 'Functional Patterns' = @{{ multi_select = @( {ps_tags} ) }} }} }} | ConvertTo-Json -Depth 5\n")
                
                out.write(f"try {{\n")
                out.write(f"  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/{cand_id}' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null\n")
                out.write(f"}} catch {{\n")
                out.write(f"  Write-Host 'Error on {name}:' $_.Exception.Response.StatusCode.value__\n")
                out.write(f"  $stream = $_.Exception.Response.GetResponseStream()\n")
                out.write(f"  $reader = New-Object System.IO.StreamReader($stream)\n")
                out.write(f"  Write-Host $reader.ReadToEnd()\n")
                out.write(f"}}\n\n")
                # Flush to save progress immediately
                out.flush()
                print(f"[{i}] Added PS update commands for {name} with {len(safe_pt)} patterns.")
            else:
                print(f"[{i}] No patterns generated for {name}.")

    print(f"[Python] Finished generating uploads2.ps1 for backfills.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "parse":
        parse_and_generate_uploads()
    else:
        orchestrate_powershell_backfill()
