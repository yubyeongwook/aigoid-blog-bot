import os
import sys
import requests
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from publishers.blogger_publisher import get_access_token, BLOG_ID

POST_ID = "5363273296052033194"

def main():
    token = get_access_token()
    if not token:
        print("Blogger 토큰 획득 실패")
        return

    print("Fetching post...")
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{POST_ID}"
    headers = {"Authorization": f"Bearer {token}"}
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"포스트 로드 실패: {res.text}")
        return

    post_data = res.json()
    content = post_data.get("content", "")

    # Replace numbers (multiplying by 10)
    replacements = [
        ("245,000원", "2,450,000원"),
        ("265,000원", "2,650,000원"),
        ("232,000원", "2,320,000원"),
        ("217,100원", "2,171,000원"),
        ("208,200원", "2,082,000원"),
    ]

    new_content = content
    for old, new in replacements:
        count = new_content.count(old)
        new_content = new_content.replace(old, new)
        print(f"Replaced '{old}' -> '{new}' ({count} occurrences)")

    if new_content == content:
        print("변경된 내용이 없습니다.")
        return

    # Update post
    print("Updating post...")
    update_data = {
        "title": post_data["title"],
        "content": new_content,
        "blog": {"id": BLOG_ID}
    }
    
    res_put = requests.put(url, headers=headers, json=update_data)
    if res_put.status_code == 200:
        print("✅ 블로그 포스트 수정 완료!")
    else:
        print(f"❌ 블로그 포스트 수정 실패 ({res_put.status_code}): {res_put.text}")

if __name__ == "__main__":
    main()
