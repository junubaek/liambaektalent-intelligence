import json

def main():
    path = 'golden_dataset_v9.json'
    d = json.load(open(path, encoding='utf-8'))

    new_cto_ids = [
        '0c07f1bc-8d5c-4c36-82fa-14de5ca79ba0',  # 한원식 (웨이브 CTO)
        'cf6f1c20-0b8b-4995-9abb-4b8cb81c3628',  # 이호석 (meliz CTO)
        '2bc346d4-2f24-4f12-b90a-ca75441a3e49',  # 강형구 (HANDHUG CTO)
    ]

    updated = 0
    for item in d:
        q = item.get('query','')
        if 'CTO' in q or '기술총괄' in q:
            old_ids = item.get('relevant_ids', [])
            # 기존 ID 유지 + 새 ID 추가 (중복 제거)
            merged = list(dict.fromkeys(old_ids + new_cto_ids))
            item['relevant_ids'] = merged
            print(f'[업데이트] {q}')
            print(f'  이전: {old_ids}')
            print(f'  이후: {merged}')
            updated += 1

    if updated == 0:
        # CTO 쿼리가 없으면 신규 추가
        d.append({
            'query': 'CTO 기술리더 플랫폼 서버 아키텍처 스타트업',
            'seniority': 'SENIOR',
            'relevant_ids': new_cto_ids
        })
        print('[신규 추가] CTO 기술리더 플랫폼 서버 아키텍처 스타트업')

    json.dump(d, open(path,'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n저장 완료. 업데이트: {updated}개')

if __name__ == '__main__':
    main()
