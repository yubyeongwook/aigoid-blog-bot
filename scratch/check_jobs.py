import requests
import json

run_id = "29085593256"
url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/jobs"

res = requests.get(url)
print("Status:", res.status_code)
if res.status_code == 200:
    data = res.json()
    for job in data.get("jobs", []):
        print(f"Job: {job.get('name')}, Status: {job.get('status')}, Conclusion: {job.get('conclusion')}")
        print("Steps:")
        for step in job.get("steps", []):
            print(f"  - {step.get('name')}: {step.get('status')}, {step.get('conclusion')}")
else:
    print(res.text)
