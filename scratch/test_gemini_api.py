import os, requests, json
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def test_gemini_full():
    model = "gemini-3.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": "Hello, write one sentence."}]}],
        "generationConfig": {"maxOutputTokens": 50, "temperature": 0.3}
    }
    try:
        res = requests.post(url, json=body, timeout=20)
        print("Status Code:", res.status_code)
        if res.status_code == 200:
            print("Response JSON:")
            print(json.dumps(res.json(), indent=2))
        else:
            print("Error Response Status Code:", res.status_code)
            print("Error Body:", res.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test_gemini_full()
