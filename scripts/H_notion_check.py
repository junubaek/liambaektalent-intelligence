import json, urllib.request
def main():
    s=json.load(open('secrets.json'))
    h={'Authorization': 'Bearer ' + s['NOTION_API_KEY'], 'Notion-Version': '2022-06-28'}
    ids=['31f225671b6f8101bd8ad88c3e27136a', '31f225671b6f8103a1b2e6418b79dffd', '31f225671b6f8103a4f4e2e9dba6e2f2']
    print("Samples:\n")
    for i in ids:
        req=urllib.request.Request(f'https://api.notion.com/v1/pages/{i}', headers=h)
        res=json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        props=res.get('properties', {})
        url_props=[v['url'] for k,v in props.items() if v['type']=='url' and v['url'] and 'drive.google' in v['url']]
        print(f"Notion ID: {i} -> Drive URL: {url_props[0] if url_props else None}")
        
if __name__ == '__main__': main()
