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
    url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs?per_page=100"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    res = requests.get(url, headers=headers)
    print("Status Code:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        runs = data.get("workflow_runs", [])
        print(f"Found {len(runs)} runs:")
        for r in runs:
            print(f"Run ID: {r.get('id')}, Name: {r.get('name')}, Status: {r.get('status')}, Conclusion: {r.get('conclusion')}, Event: {r.get('event')}, Created: {r.get('created_at')}")
    else:
        print(res.text)

if __name__ == "__main__":
    main()
