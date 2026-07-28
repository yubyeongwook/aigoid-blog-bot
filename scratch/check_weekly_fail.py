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
    return None

def download_and_analyze_run(run_id, token):
    url = f"https://api.github.com/repos/yubyeongwook/aigoid-blog-bot/actions/runs/{run_id}/logs"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    print(f"\n=================== ANALYZING RUN {run_id} ===================")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        try:
            z = zipfile.ZipFile(io.BytesIO(res.content))
            for name in z.namelist():
                if name.endswith(".txt"):
                    content = z.read(name).decode("utf-8", errors="ignore")
                    lines = content.splitlines()
                    
                    print(f"\n--- Reading {name} (Total lines: {len(lines)}) ---")
                    
                    has_error = False
                    error_lines = []
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        if "error" in line_lower or "exception" in line_lower or "traceback" in line_lower or "failed" in line_lower or "missing" in line_lower or "not found" in line_lower:
                            has_error = True
                            start = max(0, i - 3)
                            end = min(len(lines), i + 6)
                            error_lines.append(f"\n[Context at line {i+1}]:")
                            for j in range(start, end):
                                marker = ">>> " if j == i else "    "
                                error_lines.append(f"{marker}{lines[j]}")
                                
                    if has_error:
                        print("Errors/Warnings detected in this log:")
                        print("\n".join(error_lines[-20:]))
                    else:
                        print("No obvious errors/warnings detected.")
                        
                    print("\nLast 30 lines of this log:")
                    for line in lines[-30:]:
                        print(line)
        except Exception as e:
            print("Error reading log zip:", e)
    else:
        print(f"Failed to fetch logs: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    token = get_github_token()
    download_and_analyze_run("29170921920", token)
