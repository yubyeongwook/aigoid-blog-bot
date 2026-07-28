import os
import requests
import json
import sys
from dotenv import load_dotenv

# Set console encoding to UTF-8
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
    print("Status Code:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("Run Status:", data.get("status"))
        print("Run Conclusion:", data.get("conclusion"))
        # Get jobs for the run
        jobs_url = data.get("jobs_url")
        print("Jobs URL:", jobs_url)
        
        jobs_res = requests.get(jobs_url, headers=headers)
        if jobs_res.status_code == 200:
            jobs_data = jobs_res.json()
            print("Jobs count:", len(jobs_data.get("jobs", [])))
            for job in jobs_data.get("jobs", []):
                print(f"Job Name: {job.get('name')}, Status: {job.get('status')}, Conclusion: {job.get('conclusion')}")
                for step in job.get("steps", []):
                    print(f"  Step: {step.get('name')}, Status: {step.get('status')}, Conclusion: {step.get('conclusion')}")
        else:
            print("Failed to get jobs:", jobs_res.text)
    else:
        print(res.text)

if __name__ == "__main__":
    main()
