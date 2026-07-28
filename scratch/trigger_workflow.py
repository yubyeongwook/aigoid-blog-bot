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
    # daily_close.yml is the filename of the workflow
    url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/workflows/trending.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "ref": "master"
    }
    
    print("Triggering workflow trending.yml on branch master...")
    res = requests.post(url, headers=headers, json=data)
    print("Status Code:", res.status_code)
    if res.status_code == 204:
        print("Successfully triggered workflow!")
    else:
        print("Failed to trigger workflow:")
        print(res.text)

if __name__ == "__main__":
    main()
