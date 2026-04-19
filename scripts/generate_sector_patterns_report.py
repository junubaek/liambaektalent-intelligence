import json
import requests
from collections import Counter, defaultdict

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
NOTION_DB_ID = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def generate_report():
    print("🔍 Analyzing Sector-Pattern relationships...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    has_more = True
    next_cursor = None
    
    sector_to_patterns = defaultdict(Counter)
    total_count = 0
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        
        for p in resp.get('results', []):
            if p.get('archived'): continue
            total_count += 1
            props = p['properties']
            
            sectors = [s['name'] for s in props.get('Primary Sector', {}).get('multi_select', [])]
            patterns = [pt['name'] for pt in props.get('Experience Patterns', {}).get('multi_select', [])]
            
            if not sectors: sectors = ["Unclassified"]
            
            for s in sectors:
                for pt in patterns:
                    sector_to_patterns[s][pt] += 1
                    
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')
        print(f"  Processed {total_count} pages...")

    # Write Markdown Report
    report_path = "sector_patterns_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Sector-Experience Patterns Correlation Report\n\n")
        f.write("이 보고서는 노션 허브의 데이터를 바탕으로 각 섹터별 상위 10개 핵심 패턴을 요약합니다.\n\n")
        
        for sector in sorted(sector_to_patterns.keys()):
            f.write(f"## 🏢 Sector: {sector}\n")
            f.write("| Rank | Experience Pattern | Count | Percentage |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            top_patterns = sector_to_patterns[sector].most_common()
            sector_total = sum(sector_to_patterns[sector].values())
            
            for i, (pt, count) in enumerate(top_patterns, 1):
                pct = (count / sector_total * 100) if sector_total > 0 else 0
                f.write(f"| {i} | {pt} | {count} | {pct:.1f}% |\n")
            f.write("\n")
            
    print(f"✅ Report generated: {report_path}")

if __name__ == "__main__":
    generate_report()
