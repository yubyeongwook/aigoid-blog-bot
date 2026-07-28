import sys, os, requests
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from publishers.blogger_publisher import get_access_token

token = get_access_token()
blog_id = os.getenv("BLOG_ID")
url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?maxResults=15"
headers = {"Authorization": f"Bearer {token}"}

res = requests.get(url, headers=headers).json()
items = res.get("items", [])
print(f"총 {len(items)}개 글 검색됨:")
for item in items:
    print(f"- ID: {item['id']} | 제목: {item['title']} | URL: {item['url']}")
