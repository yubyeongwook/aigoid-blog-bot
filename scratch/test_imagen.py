import os, requests, json
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def test_imagen():
    if not GEMINI_API_KEY:
        print("No GEMINI_API_KEY found.")
        return
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:generateImages?key={GEMINI_API_KEY}"
    body = {
        "prompt": "A modern financial chart showing growth, dark background, golden line, clean editorial style",
        "numberOfImages": 1,
        "aspectRatio": "16:9"
    }
    
    try:
        res = requests.post(url, json=body, timeout=30)
        print("Status Code:", res.status_code)
        if res.status_code == 200:
            print("SUCCESS!")
            # The response format typically contains base64 image bytes in "generatedImages"
            data = res.json()
            if "generatedImages" in data:
                print("Generated images count:", len(data["generatedImages"]))
            else:
                print("Response data:", json.dumps(data, indent=2)[:500])
        else:
            print("Response:", res.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_imagen()
