import sys, os, requests, json
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from dotenv import load_dotenv
load_dotenv()

from publishers.blogger_publisher import get_access_token, BLOG_ID

def main():
    token = get_access_token()
    post_id = "9099326698861714150"
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        content = data.get("content", "")
        with open("scratch/afternoon_post_content.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Success: Saved content to scratch/afternoon_post_content.html")
    else:
        print("Failed:", res.text)

if __name__ == "__main__":
    main()
