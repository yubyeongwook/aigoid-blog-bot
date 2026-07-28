import os

log_path = r"C:\Users\aigoi\.gemini\antigravity-ide\brain\383b13c7-1fa3-4294-8597-5ef177527701\.system_generated\tasks\task-410.log"
dest_path = "scratch/log_410_clean.txt"

if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    with open(dest_path, "w", encoding="utf-8") as f_dest:
        f_dest.write(content)
    print("Logged copied to scratch/log_410_clean.txt")
else:
    print("Log file not found yet")
