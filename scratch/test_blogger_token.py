import os
from dotenv import load_dotenv
load_dotenv()

print("BLOG_ID:", os.getenv("BLOG_ID"))
print("CLIENT_ID:", os.getenv("GOOGLE_CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("GOOGLE_CLIENT_SECRET")[:5] if os.getenv("GOOGLE_CLIENT_SECRET") else None)
print("REFRESH_TOKEN:", os.getenv("GOOGLE_REFRESH_TOKEN")[:10] if os.getenv("GOOGLE_REFRESH_TOKEN") else None)

import requests
url = "https://oauth2.googleapis.com/token"
data = {
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
    "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
    "grant_type": "refresh_token"
}
res = requests.post(url, data=data)
print("Response Status Code:", res.status_code)
print("Response Text:", res.text)
