import os
import requests
import json
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def search_news(query):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": 10, "sort": "date"}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    else:
        print(f"Error ({res.status_code}): {res.text}")
        return []

print("=== Search for 'SK하이닉스 삼성전자 HBM' ===")
for item in search_news("SK하이닉스 삼성전자 HBM"):
    print("- Title:", item['title'].replace("<b>","").replace("</b>",""))
    print("  Desc:", item['description'].replace("<b>","").replace("</b>",""))
