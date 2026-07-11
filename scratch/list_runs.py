import requests

url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs?per_page=5"
res = requests.get(url)
print("Status:", res.status_code)
if res.status_code == 200:
    runs = res.json().get("workflow_runs", [])
    for run in runs:
        print(f"ID: {run.get('id')}")
        print(f"Name: {run.get('name')}")
        print(f"  Trigger Event: {run.get('event')}")
        print(f"  Status: {run.get('status')}, Conclusion: {run.get('conclusion')}")
        print(f"  Created At: {run.get('created_at')}") # 트리거된 시각
        print(f"  Run Started At: {run.get('run_started_at')}") # 실제 러너가 돌기 시작한 시각
        print(f"  Updated At: {run.get('updated_at')}")
        print("-" * 50)
else:
    print(res.text)
