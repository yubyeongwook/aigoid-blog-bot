import os
import requests
import json
import sys
from dotenv import load_dotenv
from datetime import datetime, timezone

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
    url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs?per_page=30"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        runs = data.get("workflow_runs", [])
        for r in runs:
            created_at = r.get("created_at")
            print(f"Run ID: {r.get('id')}\n  Name: {r.get('name')}\n  Status: {r.get('status')}\n  Conclusion: {r.get('conclusion')}\n  Event: {r.get('event')}\n  Created: {created_at}\n  Path: {r.get('path')}\n")
    else:
        print(res.text)

if __name__ == "__main__":
    main()
