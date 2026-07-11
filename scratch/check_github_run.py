import requests
import json

url = "https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/29085593256"
res = requests.get(url)
print("Status Code:", res.status_code)
if res.status_code == 200:
    data = res.json()
    print("Conclusion:", data.get("conclusion"))
    print("Event:", data.get("event"))
    print("Repository is private:", data.get("repository", {}).get("private"))
else:
    print(res.text)
