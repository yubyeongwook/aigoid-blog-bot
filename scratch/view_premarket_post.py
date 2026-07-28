import sys, os, requests, json
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from dotenv import load_dotenv
load_dotenv()

from publishers.blogger_publisher import get_access_token, BLOG_ID

def main():
    token = get_access_token()
    post_id = "3256743942301402216"
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        content = data.get("content", "")
        print("Content length:", len(content))
        with open("scratch/post_info.txt", "w", encoding="utf-8") as f:
            f.write(f"Length: {len(content)}\n")
            f.write(f"First 1000 chars:\n{content[:1000]}\n")
            f.write(f"\nLast 1000 chars:\n{content[-1000:]}\n")
        print("Success: Saved to scratch/post_info.txt")
    else:
        print("Failed:", res.text)

if __name__ == "__main__":
    main()
