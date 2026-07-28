import os, requests, sys, zipfile
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
    run_id = "29705505006"
    url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/logs"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    print(f"Fetching logs for morning run {run_id}...")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        zip_path = "scratch/morning_run_logs.zip"
        with open(zip_path, "wb") as f:
            f.write(res.content)
        
        extract_dir = "scratch/extracted_morning_logs"
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        target_log = os.path.join(extract_dir, "0_daily_v4.txt")
        dest_path = "scratch/morning_workflow_log_clean.txt"
        
        if os.path.exists(target_log):
            with open(target_log, "r", encoding="utf-8", errors="ignore") as log_f:
                content = log_f.read()
            with open(dest_path, "w", encoding="utf-8") as f_dest:
                f_dest.write(content)
            print("Successfully saved clean log to scratch/morning_workflow_log_clean.txt")
        else:
            # Let's list files in extract_dir to find the log name
            files = os.listdir(extract_dir)
            print("Log files found:", files)
    else:
        print("Failed:", res.text)

if __name__ == "__main__":
    main()
