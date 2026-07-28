import os, requests, sys
from dotenv import load_dotenv
load_dotenv()

def get_github_token():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "token=ghp_" in line:
                    return line.split("token=")[1].strip()
    return None

def main():
    token = get_github_token()
    run_id = "29710479477"
    url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/logs"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    print(f"Fetching logs for run {run_id}...")
    res = requests.get(url, headers=headers)
    print("Status:", res.status_code)
    if res.status_code == 200:
        # The logs are returned as a zip file redirect, or a zip file itself
        # Let's save the zip file
        with open("scratch/run_logs.zip", "wb") as f:
            f.write(res.content)
        print("Saved logs zip to scratch/run_logs.zip")
    else:
        print("Failed:", res.text)

if __name__ == "__main__":
    main()
