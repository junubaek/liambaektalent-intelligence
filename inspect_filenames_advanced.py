import sqlite3
import json
import os

def main():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    ids = ['bb55fc1a-c237-433e-9ef6-e79584cbb347', '83fd1454-3319-49d4-9b02-72de5fa65487']

    for cid in ids:
        cur.execute("SELECT * FROM candidates WHERE id=?", (cid,))
        r = cur.fetchone()
        if r:
            # zip with column names
            cur.execute("PRAGMA table_info(candidates)")
            cols = [c[1] for c in cur.fetchall()]
            row_dict = dict(zip(cols, r))
            print(f"\n=== Row for {row_dict['name_kr']} ({cid}) ===")
            for k, v in row_dict.items():
                if k != 'raw_text':  # raw_text is too long
                    print(f"  {k}: {v}")
        else:
            print(f"ID {cid} not found in DB")

    # Search in notion_file_map.json or drive_links_map.json if they exist
    for map_file in ['drive_links_map.json', 'notion_file_map.json', 'not_found.json']:
        if os.path.exists(map_file):
            print(f"\n--- Searching in {map_file} ---")
            try:
                data = json.load(open(map_file, encoding='utf-8'))
                # data can be dict or list
                if isinstance(data, dict):
                    for k, v in data.items():
                        str_k, str_v = str(k), str(v)
                        if any(cid in str_k or cid in str_v for cid in ids) or any('백명석' in str_k or '백명석' in str_v or '류혁곤' in str_k or '류혁곤' in str_v for cid in ids):
                            print(f"  Key: {k[:100]} | Value: {str(v)[:150]}")
                elif isinstance(data, list):
                    for idx, item in enumerate(data):
                        str_item = str(item)
                        if any(cid in str_item for cid in ids) or any('백명석' in str_item or '류혁곤' in str_item for cid in ids):
                            print(f"  [{idx}]: {str(item)[:200]}")
            except Exception as e:
                print(f"Error reading {map_file}: {e}")

    conn.close()

if __name__ == '__main__':
    main()
