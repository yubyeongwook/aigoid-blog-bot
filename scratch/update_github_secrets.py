import os
import requests
import json
import base64
from nacl import encoding, public
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.environ.get("GH_DISPATCH_TOKEN")
if not token and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "token=ghp_" in line:
                token = line.split("token=")[1].strip()

repo = "yubyeongwook/aigoid-blog-bot"

secrets_to_update = {
    "META_ACCESS_TOKEN": os.environ.get("META_ACCESS_TOKEN"),
    "INSTAGRAM_ACCOUNT_ID": os.environ.get("INSTAGRAM_ACCOUNT_ID"),
    "GOOGLE_REFRESH_TOKEN": os.environ.get("GOOGLE_REFRESH_TOKEN")
}

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

key_url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
res = requests.get(key_url, headers=headers)

if res.status_code == 200:
    key_data = res.json()
    key_id = key_data["key_id"]
    public_key_b64 = key_data["key"]
    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    
    for sec_name, sec_val in secrets_to_update.items():
        if not sec_val:
            continue
        encrypted = sealed_box.encrypt(sec_val.encode("utf-8"))
        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
        secret_url = f"https://api.github.com/repos/{repo}/actions/secrets/{sec_name}"
        body = {"encrypted_value": encrypted_b64, "key_id": key_id}
        s_res = requests.put(secret_url, headers=headers, json=body)
        print(f"Secret {sec_name} update status: {s_res.status_code}")
        if s_res.status_code in (201, 204):
            print(f"✅ Successfully updated GitHub Secret: {sec_name}")
else:
    print("Failed to get public key:", res.text)
