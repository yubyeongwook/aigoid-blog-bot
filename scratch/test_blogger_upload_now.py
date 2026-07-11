import sys, os, requests
sys.path.append(r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot")
from publishers.blogger_publisher import get_access_token, BLOG_ID

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

token = get_access_token()
if not token:
    print("Token failed")
    sys.exit(1)

image_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\assets\brand_banner.png"
url = f"https://www.googleapis.com/upload/blogger/v3/blogs/{BLOG_ID}/images"
headers = {
    "Authorization": f"Bearer {token}",
}
files = {
    "image": ("image.png", open(image_path, "rb"), "image/png")
}

print("Attempting upload to Blogger API...")
res = requests.post(url, headers=headers, files=files)
print("Status Code:", res.status_code)
print("Response:", res.text)
