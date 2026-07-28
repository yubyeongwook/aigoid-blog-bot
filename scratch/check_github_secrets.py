import os
import requests
import json
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_github_token():
    load_dotenv()
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "token=ghp_" in line:
                    return line.split("token=")[1].strip()
    return None

def main():
    token = get_github_token()
    url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/secrets"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    res = requests.get(url, headers=headers)
    print("Status Code:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        secrets = data.get("secrets", [])
        print(f"Found {len(secrets)} secrets:")
        for s in secrets:
            print(f"Name: {s.get('name')}, Created: {s.get('created_at')}, Updated: {s.get('updated_at')}")
    else:
        print("Failed to get secrets list:")
        print(res.text)

if __name__ == "__main__":
    main()
