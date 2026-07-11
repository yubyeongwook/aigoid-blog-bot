# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import sys

try:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

with open("scratch/published_raw.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
post_body = soup.find(class_="post-body")

if post_body:
    print("=== POST BODY RAW HTML END ===")
    # Print the last 1500 chars of the raw HTML of post_body
    print(str(post_body)[-1500:])
else:
    print("Post body not found!")
