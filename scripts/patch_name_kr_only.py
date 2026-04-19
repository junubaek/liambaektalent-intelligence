import re
from neo4j import GraphDatabase
from tqdm import tqdm

def get_korean_name(raw_name):
    clean = re.sub(r'\[.*?\]', '', raw_name)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = re.sub(r'부문|원본|최종|포트폴리오|이력서|합격|이력|Resume|CV', '', clean, flags=re.IGNORECASE)
    matches = re.findall(r'[가-힣]{2,4}', clean)
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','개발자','엔지니어','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용'}
    valid_matches = [m for m in matches if m not in stop_words]
    return valid_matches[-1] if valid_matches else (matches[-1] if matches else "")

def main():
    driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        print("Fetching all candidate nodes from Neo4j...")
        result = session.run("MATCH (c:Candidate) RETURN c.name AS name")
        all_node_names = [record["name"] for record in result]
        
        updated = 0
        for node_name in tqdm(all_node_names, desc="Patching name_kr"):
            name_kr = get_korean_name(node_name)
            if name_kr:
                session.run("MATCH (c:Candidate {name: $name}) SET c.name_kr = $name_kr", name=node_name, name_kr=name_kr)
                updated += 1
                
        print(f"\nDone! Updated {updated} candidates with new name_kr logic.")

if __name__ == "__main__":
    main()
