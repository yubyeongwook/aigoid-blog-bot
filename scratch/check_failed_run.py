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
    return os.environ.get("GH_DISPATCH_TOKEN")

def download_and_analyze_run(run_id, token):
    url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"token {token}"} if token else {}
        
    print(f"\n=================== ANALYZING RUN {run_id} ===================")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        try:
            z = zipfile.ZipFile(io.BytesIO(res.content))
            for name in z.namelist():
                if name.endswith(".txt"):
                    content = z.read(name).decode("utf-8", errors="ignore")
                    lines = content.splitlines()
                    print(f"\n--- Log File: {name} (Total lines: {len(lines)}) ---")
                    for line in lines[-50:]:
                        print(line)
        except Exception as e:
            print("Error reading log zip:", e)
    else:
        print(f"Failed to fetch logs: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    token = get_github_token()
    download_and_analyze_run("30157096172", token)
