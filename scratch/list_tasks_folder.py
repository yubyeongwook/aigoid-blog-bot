import os

folder = r"C:\Users\aigoi\.gemini\antigravity-ide\brain\383b13c7-1fa3-4294-8597-5ef177527701\.system_generated\tasks"
if os.path.exists(folder):
    files = os.listdir(folder)
    print("Files in tasks folder:")
    for f in files:
        p = os.path.join(folder, f)
        print(f"{f}: {os.path.getsize(p)} bytes")
else:
    print("Tasks folder does not exist:", folder)
