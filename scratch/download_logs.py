import requests
import zipfile
import io
import os

run_id = "29085593256"
url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/logs"

print("Downloading logs...")
res = requests.get(url)
print("Status Code:", res.status_code)

if res.status_code == 200:
    try:
        z = zipfile.ZipFile(io.BytesIO(res.content))
        print("Files in logs zip:")
        for name in z.namelist():
            print("-", name)
            # Print the content of log files
            if name.endswith(".txt") and "/" in name:
                content = z.read(name).decode("utf-8", errors="ignore")
                lines = content.splitlines()
                # Print last 50 lines or lines containing Error/Exception
                print("--- Content of", name, "---")
                for line in lines[-100:]:
                    print(line)
    except Exception as e:
        print("Error reading zip:", e)
else:
    print(res.text)
