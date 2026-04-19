import json

def investigate():
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    targets = [x for x in data if '장형준' in x.get('name_kr', '') or '최예리' in x.get('name_kr', '')]
    
    for t in targets:
        print(f"Name: {t.get('name_kr')}")
        print(f"  Phone: {t.get('phone', 'N/A')}")
        print(f"  Company: {t.get('current_company', 'N/A')}")
        
if __name__ == "__main__":
    investigate()
