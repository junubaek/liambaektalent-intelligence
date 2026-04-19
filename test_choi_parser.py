from dynamic_parser_v2 import parse_resume_batch, save_edges
import dynamic_parser_v2
import sqlite3

def run_choi_test():
    # 강제로 캐시 안함 (새 프롬프트 적용 위해)
    dynamic_parser_v2.cached_content_name = None
    
    # 1. Get raw text
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    row = c.execute('SELECT raw_text FROM candidates WHERE name_kr="최호진"').fetchone()
    conn.close()
    
    if not row or not row[0]:
        print("raw_text not found for 최호진")
        return
        
    raw_text = row[0]
    
    # 2. Parse batch for Choi
    batch_dict = {"최호진": raw_text}
    print("Parsing Choi Ho-jin with new prompt...")
    parsed_results = parse_resume_batch(batch_dict)
    
    edges = parsed_results.get("최호진", [])
    print(f"\n[Parsed Edges for 최호진] Count: {len(edges)}")
    
    found_openstack = False
    for edge in edges:
        action = getattr(edge, 'action', '').upper()
        skill = getattr(edge, 'skill', '')
        print(f" - ({action}) -> {skill}")
        if 'openstack' in skill.lower():
            found_openstack = True
            
    print(f"\n=> OpenStack Extracted: {found_openstack}")
    
    # 3. Save to Neo4j
    if edges:
        print("Saving to Neo4j...")
        save_edges("최호진", edges, raw_text)
        print("Saved.")
        
if __name__ == '__main__':
    run_choi_test()
