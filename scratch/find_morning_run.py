import os, requests, json
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
    url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs?per_page=100"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        runs = res.json().get("workflow_runs", [])
        output = []
        for r in runs:
            name = r.get("name", "")
            if "오전 7시 브리핑" in name:
                line = f"Run ID: {r.get('id')}, Name: {name}, Status: {r.get('status')}, Conclusion: {r.get('conclusion')}, Event: {r.get('event')}, Created: {r.get('created_at')}"
                output.append(line)
        
        with open("scratch/morning_runs_filtered.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print("Saved filtered runs to scratch/morning_runs_filtered.txt")
    else:
        print("Failed:", res.text)

if __name__ == "__main__":
    main()
