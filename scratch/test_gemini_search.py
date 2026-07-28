import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GEMINI_API_KEY", "")
if not key:
    print("No GEMINI_API_KEY found")
    exit(1)

model = "gemini-2.5-flash"  # or gemini-3.5-flash
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

body = {
    "contents": [{"parts": [{"text": "오늘 한국 시장에서 가장 화제가 된 코스피 종목과 그 이유를 설명해줘. 최신 정보를 인터넷에서 검색해서 알려줘."}]}],
    "tools": [{"googleSearch": {}}],
    "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.3}
}

try:
    res = requests.post(url, json=body, timeout=30)
    print("Status:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("Response Keys:", data.keys())
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                print("Generated Text:\n", parts[0].get("text"))
            
            # Print search metadata if any
            metadata = candidates[0].get("groundingMetadata", {})
            if metadata:
                print("\nGrounding Metadata Keys:", metadata.keys())
                queries = metadata.get("webSearchQueries", [])
                print("Search queries used:", queries)
        else:
            print("No candidates:", data)
    else:
        print("Error:", res.text)
except Exception as e:
    print("Exception:", e)
