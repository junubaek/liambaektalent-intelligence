import requests
import json

def run():
    url = "http://127.0.0.1:7474/db/neo4j/tx/commit"
    
    query = """
    MATCH (c:Candidate)
    WHERE c.name_kr IN ['김대용', '김용']
    RETURN c.id, c.document_hash, c.phone, c.email
    """
    
    payload = {
        "statements": [
            {
                "statement": query
            }
        ]
    }
    
    response = requests.post(url, json=payload, auth=("neo4j", "toss1234"))
    
    if response.status_code == 200:
        data = response.json()
        results = data['results'][0]['data']
        print(f"{'id':<18} | {'document_hash':<35} | {'phone':<15} | {'email':<20}")
        print("-" * 100)
        count = 0
        for row in results:
            r = row['row']
            print(f"{str(r[0]):<18} | {str(r[1]):<35} | {str(r[2]):<15} | {str(r[3]):<20}")
            count += 1
        print(f"\nTotal match: {count}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    run()
