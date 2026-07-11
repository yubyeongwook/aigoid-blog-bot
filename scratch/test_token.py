import os, requests, json
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

url = "https://oauth2.googleapis.com/token"
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH_TOKEN,
    "grant_type": "refresh_token"
}

try:
    res = requests.post(url, data=data, timeout=10)
    print("Status Code:", res.status_code)
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("Error:", e)
