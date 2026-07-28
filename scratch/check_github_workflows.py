import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("GH_DISPATCH_TOKEN")
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "token=ghp_" in line:
                token = line.split("token=")[1].strip()

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

res = requests.get("https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/workflows", headers=headers)
print("Workflows status code:", res.status_code)
if res.status_code == 200:
    for wf in res.json().get("workflows", []):
        print(f"ID: {wf['id']}, Name: {wf['name']}, State: {wf['state']}, Path: {wf['path']}")

runs_res = requests.get("https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs?per_page=30", headers=headers)
if runs_res.status_code == 200:
    print("\n--- Recent Runs ---")
    for r in runs_res.json().get("workflow_runs", []):
        print(f"RunID: {r['id']}, Name: {r['name']}, Conclusion: {r['conclusion']}, Event: {r['event']}, Created: {r['created_at']}")
