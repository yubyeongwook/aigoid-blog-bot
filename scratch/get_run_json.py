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
    run_id = "29192160729"
    url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        # print specific fields or the whole json in a formatted way
        # filter out very large fields if any
        print(json.dumps(data, indent=2))
    else:
        print(res.text)

if __name__ == "__main__":
    main()
