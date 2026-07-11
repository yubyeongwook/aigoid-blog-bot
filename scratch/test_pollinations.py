import requests
prompt = "Minimalist financial chart on dark background, signal gold accent, rise green line, high contrast"
encoded_prompt = requests.utils.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&private=true"
print("Requesting from Pollinations AI...")
res = requests.get(url, timeout=30)
print("Status Code:", res.status_code)
print("Image size in bytes:", len(res.content))
