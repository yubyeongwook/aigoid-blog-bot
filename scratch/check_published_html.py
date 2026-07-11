import requests
from bs4 import BeautifulSoup
import sys

try:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

url = "https://aigoid.blogspot.com/2026/07/07-11_0404362699.html"
res = requests.get(url)
html = res.text

# Save raw HTML
with open("scratch/published_raw.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Saved raw HTML to scratch/published_raw.html")

soup = BeautifulSoup(html, "html.parser")
post_body = soup.find(class_="post-body")

if post_body:
    text = post_body.text
    print("Post body length:", len(text))
    
    # Check keywords
    keywords = {
        "meotjaengi": "멋쟁이",
        "sigag": "시각",
        "pick": "픽",
        "tuja": "투자",
        "disclaimer": "Disclaimer",
        "goji": "고지",
        "avoid": "피할",
        "scenario": "시나리오"
    }

    for key, val in keywords.items():
        count = text.count(val)
        print(f"{key} ({val}): {count} times")
        
    print("\n=== Headings in the HTML ===")
    for tag in post_body.find_all(["h1", "h2", "h3"]):
        print(f"<{tag.name}>: {tag.text.strip()}")
        
    print("\n=== Last 800 chars of Post Body ===")
    print(text[-800:])
else:
    print("Post body not found!")
