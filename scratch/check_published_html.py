import requests
url = "https://aigoid.blogspot.com/2026/07/07-11_0320410973.html"
res = requests.get(url)
with open("scratch/published_raw.html", "w", encoding="utf-8") as f:
    f.write(res.text)
print("Saved raw HTML to scratch/published_raw.html")
