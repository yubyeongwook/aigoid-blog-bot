import os
log_path = r"C:\Users\aigoi\.gemini\antigravity-ide\brain\383b13c7-1fa3-4294-8597-5ef177527701\.system_generated\tasks\task-237.log"
dest_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\scratch\log_utf8.txt"
if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    with open(dest_path, "w", encoding="utf-8") as f_dest:
        f_dest.write(content)
    print("Copied log successfully to scratch/log_utf8.txt")
else:
    print("Log file not found")
