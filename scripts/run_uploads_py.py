import re
import json
import urllib.request
import urllib.error

# Regex to find all blocks like:
# Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8114-9122-fee5c551a609' ... -Body $p
# And where $p is defined as:
# $p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'A' }, @{ name = 'B' } ) } } } | ConvertTo-Json -Depth 5

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

NOTION_API_KEY = secrets["NOTION_API_KEY"].strip()

with open("uploads2.ps1", "r", encoding="utf-8") as f:
    content = f.read()

# Find each page ID and its corresponding tags
# Pattern matches Write-Host 'Updating <id>' followed by the tags
blocks = content.split("Write-Host 'Updating ")

success_count = 0
error_count = 0

for block in blocks[1:]:
    lines = block.strip().split('\n')
    page_id = lines[0].strip("'")
    
    # Find the line with the tags
    tags_line = next((l for l in lines if "$p = " in l), None)
    if not tags_line: continue
    
    # Extract tags names: @{ name = 'Some Tag' }
    tags = re.findall(r"@\{\s*name\s*=\s*'([^']+)'\s*\}", tags_line)
    
    # Unescape PowerShell quotes
    tags = [t.replace("''", "'") for t in tags]
    
    # Construct Notion API Payload
    payload = {
        "properties": {
            "Functional Patterns": {
                "multi_select": [{"name": t} for t in tags]
            }
        }
    }
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='PATCH')
    
    print(f"Updating {page_id} with {len(tags)} patterns...")
    try:
        with urllib.request.urlopen(req) as response:
            success_count += 1
    except urllib.error.HTTPError as e:
        print(f"Error {e.code} on {page_id}: {e.read().decode('utf-8')}")
        error_count += 1
    except Exception as e:
        print(f"Error on {page_id}: {e}")
        error_count += 1

print(f"\nUpload complete. Success: {success_count}, Errors: {error_count}")
