import sqlite3

def check_raw_text():
    try:
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        c.execute("SELECT raw_text FROM candidates WHERE name_kr = '오원교'")
        row = c.fetchone()
        if row:
            raw_text = row[0]
            print("=== 오원교 raw_text 선두 1500자 ===")
            print(raw_text[:1500])
            
            print("\n=== 키워드 존재 여부 ===")
            print("Kubernetes:", "kubernetes" in raw_text.lower())
            print("Terraform:", "terraform" in raw_text.lower())
            print("LangGraph:", "langgraph" in raw_text.lower())
        else:
            print("오원교님을 DB에서 찾을 수 없습니다.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_raw_text()
