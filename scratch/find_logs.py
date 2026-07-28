import os
base = r"C:\Users\aigoi\.gemini\antigravity-ide\brain\383b13c7-1fa3-4294-8597-5ef177527701"
print(f"Walking directory: {base}")
if os.path.exists(base):
    for root, dirs, files in os.walk(base):
        for f in files:
            path = os.path.join(root, f)
            print(path)
else:
    print("Base directory does not exist")
