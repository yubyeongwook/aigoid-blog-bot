"""
멋쟁이 인사이트 — 인스타그램 자동 카드뉴스 발행
Gemini API로 카드뉴스 이미지 생성 → Instagram Graph API로 자동 업로드
"""

import os
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
import tempfile
from pathlib import Path


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
INSTAGRAM_API_URL = "https://graph.instagram.com/v21.0"


def generate_card_image_prompt(title: str, content: str, stars: str = "") -> str:
    return f"""
한국 주식/투자 전문 SNS 카드뉴스 이미지를 만들어줘.

스타일:
- 배경: 짙은 네이비 (#0A0E1A)
- 강조색: 밝은 시안 (#00D4FF)
- 텍스트: 흰색
- 우상단: 멋쟁이 인사이트 SMART MONEY INTELLIGENCE 로고
- 좌하단: aigoid.blogspot.com
- 전문적이고 세련된 금융 매거진 스타일
- 정사각형 (1:1 비율)

내용:
제목: {title}
{f'신뢰도: {stars}' if stars else ''}
핵심 내용: {content[:200]}

이미지 안에 텍스트를 명확하게 배치해줘.
"""


def call_gemini_image(api_key: str, prompt: str) -> bytes | None:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_API_URL}?key={api_key}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        for part in result.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                return base64.b64decode(part["inlineData"]["data"])
    except Exception as e:
        print(f"Gemini 이미지 생성 실패: {e}")
    return None


def upload_image_to_instagram(
    account_id: str, access_token: str, image_url: str, caption: str
) -> str | None:
    # 1단계: 미디어 컨테이너 생성
    params = urllib.parse.urlencode({
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    })
    url = f"{INSTAGRAM_API_URL}/{account_id}/media"
    req = urllib.request.Request(
        url, data=params.encode(), method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            container_id = json.loads(resp.read())["id"]
    except Exception as e:
        print(f"미디어 컨테이너 생성 실패: {e}")
        return None

    # 2단계: 게시물 발행
    params = urllib.parse.urlencode({
        "creation_id": container_id,
        "access_token": access_token,
    })
    url = f"{INSTAGRAM_API_URL}/{account_id}/media_publish"
    req = urllib.request.Request(
        url, data=params.encode(), method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            post_id = json.loads(resp.read())["id"]
            return f"https://www.instagram.com/p/{post_id}/"
    except Exception as e:
        print(f"Instagram 발행 실패: {e}")
        return None


def save_temp_image(image_bytes: bytes) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp.write(image_bytes)
    tmp.close()
    return tmp.name


def post_to_instagram(title: str, content: str, caption: str, stars: str = "") -> dict:
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    access_token = os.environ.get("META_ACCESS_TOKEN", "")
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

    if not all([gemini_key, access_token, account_id]):
        return {"success": False, "error": "환경변수 미설정"}

    # 이미지 생성
    prompt = generate_card_image_prompt(title, content, stars)
    image_bytes = call_gemini_image(gemini_key, prompt)
    if not image_bytes:
        return {"success": False, "error": "이미지 생성 실패"}

    # 임시 파일로 저장 (실제 서비스에서는 S3 등 퍼블릭 URL 필요)
    # GitHub Actions에서는 이미지를 공개 URL로 올려야 함
    # 여기서는 imgbb.com 무료 이미지 호스팅 사용
    imgbb_key = os.environ.get("IMGBB_API_KEY", "")
    if not imgbb_key:
        return {"success": False, "error": "IMGBB_API_KEY 미설정 — 이미지 호스팅 필요"}

    # imgbb에 이미지 업로드
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    params = urllib.parse.urlencode({"key": imgbb_key, "image": encoded})
    req = urllib.request.Request(
        "https://api.imgbb.com/1/upload",
        data=params.encode(), method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            img_url = json.loads(resp.read())["data"]["url"]
    except Exception as e:
        return {"success": False, "error": f"이미지 업로드 실패: {e}"}

    # 인스타그램 발행
    post_url = upload_image_to_instagram(account_id, access_token, img_url, caption)
    if post_url:
        return {"success": True, "post_url": post_url, "image_url": img_url}
    return {"success": False, "error": "Instagram 발행 실패"}


if __name__ == "__main__":
    result = post_to_instagram(
        title="테스트 카드뉴스",
        content="멋쟁이 인사이트 자동화 테스트입니다.",
        caption="📊 멋쟁이 인사이트 테스트\n#주식 #투자 #코스피 #미국주식",
        stars="★★★★★"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
