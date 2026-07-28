import zipfile, os

zip_path = "scratch/run_logs.zip"
extract_dir = "scratch/extracted_logs"
os.makedirs(extract_dir, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Save the target step log content to a clean UTF-8 file
target_log = os.path.join(extract_dir, "0_premarket_v4.txt")
dest_path = "scratch/workflow_log_clean.txt"

if os.path.exists(target_log):
    with open(target_log, "r", encoding="utf-8", errors="ignore") as log_f:
        content = log_f.read()
    with open(dest_path, "w", encoding="utf-8") as f_dest:
        f_dest.write(content)
    print("Successfully wrote log to scratch/workflow_log_clean.txt")
else:
    print("Target log file not found in zip")
