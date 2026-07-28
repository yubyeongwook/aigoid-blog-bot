"""
wordpress_publisher.py — WordPress 자동 발행 엔진
WordPress REST API v2 + Application Password 인증
"""
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WORDPRESS_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USER", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")

def get_wp_auth():
    if not WP_USER or not WP_APP_PASSWORD:
        return None
    return HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

def get_or_create_tag(tag_name: str) -> int:
    auth = get_wp_auth()
    if not auth or not WP_URL:
        return None
    
    url = f"{WP_URL}/wp-json/wp/v2/tags"
    try:
        # Search tag
        res = requests.get(url, params={"search": tag_name}, auth=auth, timeout=10)
        if res.status_code == 200:
            tags = res.json()
            for t in tags:
                if t["name"].lower() == tag_name.lower():
                    return t["id"]
        
        # Create tag if not exists
        res_post = requests.post(url, json={"name": tag_name}, auth=auth, timeout=10)
        if res_post.status_code == 201:
            return res_post.json().get("id")
    except Exception as e:
        print(f"워드프레스 태그 관리 오류 ({tag_name}): {e}")
    return None

def get_or_create_category(cat_name: str) -> int:
    auth = get_wp_auth()
    if not auth or not WP_URL:
        return None
    
    url = f"{WP_URL}/wp-json/wp/v2/categories"
    try:
        # Search category
        res = requests.get(url, params={"search": cat_name}, auth=auth, timeout=10)
        if res.status_code == 200:
            cats = res.json()
            for c in cats:
                if c["name"].lower() == cat_name.lower():
                    return c["id"]
        
        # Create category if not exists
        res_post = requests.post(url, json={"name": cat_name}, auth=auth, timeout=10)
        if res_post.status_code == 201:
            return res_post.json().get("id")
    except Exception as e:
        print(f"워드프레스 카테고리 관리 오류 ({cat_name}): {e}")
    return None

def publish_post(title: str, html_content: str,
                 labels: list = None, draft: bool = False,
                 published_time: str = None) -> dict:
    """
    워드프레스에 포스트를 발행합니다.
    Blogger 퍼블리셔(blogger_publisher.py)와 100% 호환되는 시그니처를 제공합니다.
    """
    auth = get_wp_auth()
    if not auth or not WP_URL:
        return {"error": "워드프레스 인증 설정 누락 (WORDPRESS_URL, USER, APP_PASSWORD)"}

    url = f"{WP_URL}/wp-json/wp/v2/posts"
    
    # Resolve tags (labels)
    tag_ids = []
    if labels:
        for label in labels:
            tid = get_or_create_tag(label)
            if tid:
                tag_ids.append(tid)

    # Assign default category (e.g. "멋쟁이인사이트")
    cat_id = get_or_create_category("멋쟁이인사이트")
    categories = [cat_id] if cat_id else []

    status = "draft" if draft else "publish"
    
    payload = {
        "title": title,
        "content": html_content,
        "status": status,
        "tags": tag_ids,
        "categories": categories
    }

    if published_time:
        # format: ISO 8601 (e.g. 2026-07-15T21:00:00)
        payload["date"] = published_time

    try:
        res = requests.post(url, json=payload, auth=auth, timeout=15)
        if res.status_code in [200, 201]:
            data = res.json()
            print(f"✅ 워드프레스 발행 완료: {data.get('link')}")
            return {
                "id": data.get("id"),
                "url": data.get("link"),
                "status": data.get("status")
            }
        else:
            return {"error": f"발행 실패 ({res.status_code}): {res.text}"}
    except Exception as e:
        print(f"워드프레스 API 통신 오류: {e}")
        return {"error": str(e)}
