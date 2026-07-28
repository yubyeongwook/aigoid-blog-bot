import sys, os, requests
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from publishers.blogger_publisher import get_access_token

token = get_access_token()
blog_id = os.getenv("BLOG_ID")
post_id_to_delete = "2360716995345197355" # 중복 장전 브리핑 테스트글

url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{post_id_to_delete}"
headers = {"Authorization": f"Bearer {token}"}

res = requests.delete(url, headers=headers)
if res.status_code in [200, 204]:
    print(f"[SUCCESS] 중복 테스트글({post_id_to_delete}) 삭제 성공!")
else:
    print(f"[FAIL] 삭제 응답 코드: {res.status_code}, {res.text}")
