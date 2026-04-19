import os
import glob
import re
import pdfplumber
from neo4j import GraphDatabase

def get_years_from_text(text):
    """
    Extracts total years from text by parsing date ranges.
    Looks for patterns like YYYY~YYYY, YYYY.MM~YYYY.MM, etc.
    """
    # Look for 4 digit years
    years = map(int, re.findall(r'\b(20[0-2][0-9]|19[8-9][0-9])\b', text))
    years = list(years)
    if not years:
        # Check for 2 digit years like 17.03 ~ 22.01
        matches = re.findall(r'\b([0-2][0-9])\.[0-1][0-9]\b', text)
        for m in matches:
            y = int(m)
            if y <= 26:
                years.append(2000 + y)
            elif y >= 80:
                years.append(1900 + y)
    
    if not years:
        return 0
        
    min_year = min(years)
    max_year = max(years)
    
    # Simple sanity check
    if max_year > 2026: max_year = 2026
    if min_year < 1980: min_year = min(y for y in years if y >= 1980) if any(y >= 1980 for y in years) else 1980
    if min_year > max_year:
        return 0
        
    return max_year - min_year

def calculate_seniority(years):
    if years <= 4:
        return "Junior"
    elif years <= 9:
        return "Middle"
    else:
        return "Senior"

def main():
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))
    
    print("Indexing local PDFs...")
    pdf_dir = os.path.abspath(os.path.join("..", "02_resume 전처리"))
    all_pdfs = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
    pdf_map = {}
    for p in all_pdfs:
        filename = os.path.basename(p)
        clean_name = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', filename).replace('부문', '').replace('원본', '').strip()
        pdf_map[clean_name] = p
        
    print(f"Found {len(all_pdfs)} PDFs.")

    with driver.session() as session:
        result = session.run("MATCH (c:Candidate) RETURN elementId(c) AS node_id, c.name AS name, c.name_kr AS name_kr, c.total_years AS total_years")
        nodes = [dict(record) for record in result]
    import concurrent.futures

    print(f"Fetched {len(nodes)} candidates from Neo4j.")
    
    missing_years_count = 0
    
    def process_node(row):
        node_id = row["node_id"]
        raw_name = row["name"] or ""
        name_kr = row["name_kr"] or ""
        total_years = row["total_years"]
        
        is_missing = False
        if total_years is None:
            is_missing = True
            clean_name = name_kr if name_kr else re.sub(r'\[.*?\]|\(.*?\)|\..*', '', raw_name).replace('부문', '').replace('원본', '').strip()
            
            matched_pdf = None
            for key, path in pdf_map.items():
                if clean_name and (clean_name in key or key in clean_name):
                    matched_pdf = path
                    break
            
            calc_years = 0
            if matched_pdf:
                try:
                    with pdfplumber.open(matched_pdf) as pdf:
                        text = ''.join(page.extract_text() or '' for page in pdf.pages)
                        calc_years = get_years_from_text(text)
                except Exception as e:
                    pass
            total_years = float(calc_years)
        else:
            total_years = float(total_years)
            
        seniority = calculate_seniority(total_years)
        return node_id, total_years, seniority, is_missing

    updated_count = 0
    stats = {"Junior": 0, "Middle": 0, "Senior": 0}
    
    print("Processing nodes using ThreadPoolExecutor...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_node, row) for row in nodes]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results.append(res)
            updated_count += 1
            if updated_count % 100 == 0:
                print(f"Processed {updated_count}/{len(nodes)}")

    print("Updating Neo4j with processed data...")
    with driver.session() as session:
        for res in results:
            node_id, total_years, seniority, is_missing = res
            if is_missing:
                missing_years_count += 1
            stats[seniority] += 1
            
            session.run("""
            MATCH (c) WHERE elementId(c) = $node_id
            SET c.total_years = $total_years, c.seniority = $seniority
            """, node_id=node_id, total_years=total_years, seniority=seniority)

    print("\n--- Summary ---")
    print(f"Total Nodes Processed: {updated_count}")
    print(f"Calculated missing years for {missing_years_count} candidates.")
    print(f"Seniority Stats: Junior: {stats['Junior']}, Middle: {stats['Middle']}, Senior: {stats['Senior']}")

if __name__ == "__main__":
    main()
