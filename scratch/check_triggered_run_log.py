import os
import requests
import zipfile
import io
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

def download_and_analyze_run(run_id, token):
    url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/logs"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    print(f"\n=================== ANALYZING RUN {run_id} ===================")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        try:
            z = zipfile.ZipFile(io.BytesIO(res.content))
            for name in z.namelist():
                if name.endswith(".txt"):
                    content = z.read(name).decode("utf-8", errors="ignore")
                    lines = content.splitlines()
                    
                    print(f"ZIP File: {name}")
                    if name.endswith(".txt") and not "system.txt" in name:
                        print(f"\n--- Reading {name} (Total lines: {len(lines)}) ---")
                        for i, line in enumerate(lines):
                            if any(k in line for k in ["오류", "Error", "Exception", "발행", "API", "인스타그램", "완료", "실패", "URL"]):
                                print(f"{i}: {line}")
        except Exception as e:
            print("Error reading log zip:", e)
    else:
        print(f"Failed to fetch logs: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    token = get_github_token()
    download_and_analyze_run("29325885120", token)
