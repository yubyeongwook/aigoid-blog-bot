import requests

client_id = 'rOEILWKqOzePWRtXzDSw'
client_secret = 'mgcGdqkSk9'
url = 'https://openapi.naver.com/v1/search/news.json'
headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}

keywords = ['산재 인정', '최저임금 209시간', '주휴수당 미지급', '부당해고 수당', '퇴직금 계산기']

print("=== [REALTIME LABOR TREND REPORT] ===")
for kw in keywords:
    res = requests.get(url, headers=headers, params={'query': kw, 'display': 2, 'sort': 'date'})
    print(f"\n[HOT KEYWORD: {kw}]")
    if res.status_code == 200:
        for item in res.json().get('items', []):
            title = item['title'].replace('<b>','').replace('</b>','').replace('&quot;','"').replace('&amp;','&')
            print(f"   News: {title.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')}")
