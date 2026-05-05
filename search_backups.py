import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

def search_json(filepath, target):
    print(f"Searching in {filepath} for {target}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                results = [d for d in data if target in str(d)]
                for r in results:
                    print(f"Match: {r.get('이름') or r.get('name_kr') or 'Unknown'} | {r.get('현재소속') or r.get('current_company') or 'Unknown'}")
                    if 'google_drive_url' in r:
                        print(f"  URL: {r['google_drive_url']}")
                    elif 'drive_url' in r:
                        print(f"  URL: {r['drive_url']}")
            elif isinstance(data, dict):
                for k, v in data.items():
                    if target in str(k) or target in str(v):
                        print(f"Key Match: {k}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

targets = ['마켓로보', '김광우', '조예원', '남현승', '정소윤']
files = [
    'headhunting_engine/analytics/reparsed_pool_v1.3_elite.json',
    'headhunting_engine/analytics/reparsed_pool_v1.2.json',
    'processed_backup_20260413.json'
]

for t in targets:
    print(f"\n=== Target: {t} ===")
    for f in files:
        search_json(f, t)
