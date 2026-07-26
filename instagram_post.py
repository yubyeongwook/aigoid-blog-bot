"""
멋쟁이 인사이트 — 인스타그램 자동 카드뉴스 발행
Gemini API로 카드뉴스 이미지 생성 → Instagram Graph API로 자동 업로드
"""

import os
import json
import base64
import tempfile
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages"
INSTAGRAM_API_URL = "https://graph.facebook.com/v21.0"


def generate_card_image_prompt(title: str, content: str, stars: str = "") -> str:
    return "ultra modern minimalist financial tech art, sleek 3d glassmorphism glowing stock market chart, futuristic digital wealth sphere, dark obsidian background, electric cyan and emerald green accents, high-end finance tech magazine aesthetic, octane render, 8k resolution, photorealistic, clean composition, no text, no words, no human, no woman, no people, no face, no person"


def call_gemini_image(api_key: str, prompt: str) -> bytes | None:
    url = f"{GEMINI_API_URL}?key={api_key}"
    payload = {
        "prompt": prompt,
        "numberOfImages": 1,
        "aspectRatio": "1:1"
    }
    try:
        res = requests.post(url, json=payload, timeout=60)
        if res.status_code == 200:
            result = res.json()
            if "generatedImages" in result and len(result["generatedImages"]) > 0:
                b64_data = result["generatedImages"][0]["image"]["imageBytes"]
                return base64.b64decode(b64_data)
        else:
            print(f"Gemini API 오류 ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"Gemini 이미지 생성 실패: {e}")
    return None


def call_pollinations_image(prompt: str) -> bytes | None:
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt, safe='')}?width=1024&height=1024&nologo=true&private=true"
        print("🤖 Pollinations AI 이미지 생성 시도 중...")
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return res.content
        else:
            print(f"Pollinations AI API 오류 ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"Pollinations AI 이미지 생성 실패: {e}")
    return None


def upload_image_to_instagram(
    account_id: str, access_token: str, image_url: str, caption: str
) -> tuple[str | None, str | None]:
    # 1단계: 미디어 컨테이너 생성
    url = f"{INSTAGRAM_API_URL}/{account_id}/media"
    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }
    try:
        res = requests.post(url, data=data, timeout=30)
        if res.status_code == 200:
            container_id = res.json()["id"]
        else:
            err_msg = f"미디어 컨테이너 생성 실패 ({res.status_code}): {res.text}"
            print(f"⚠️ {err_msg}")
            return None, err_msg
    except Exception as e:
        err_msg = f"미디어 컨테이너 생성 예외: {e}"
        print(f"⚠️ {err_msg}")
        return None, err_msg

    # 2단계: 게시물 발행
    url = f"{INSTAGRAM_API_URL}/{account_id}/media_publish"
    data = {
        "creation_id": container_id,
        "access_token": access_token,
    }
    try:
        res = requests.post(url, data=data, timeout=30)
        if res.status_code == 200:
            post_id = res.json()["id"]
            return f"https://www.instagram.com/p/{post_id}/", None
        else:
            err_msg = f"Instagram 발행 실패 ({res.status_code}): {res.text}"
            print(f"⚠️ {err_msg}")
            return None, err_msg
    except Exception as e:
        err_msg = f"Instagram 발행 예외: {e}"
        print(f"⚠️ {err_msg}")
        return None, err_msg


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
        print("⚠️ Gemini 이미지 생성 실패. Pollinations AI 백업으로 시도합니다...")
        image_bytes = call_pollinations_image(prompt)

    if not image_bytes:
        return {"success": False, "error": "이미지 생성 실패"}

    # imgbb에 이미지 업로드
    imgbb_key = os.environ.get("IMGBB_API_KEY", "")
    if not imgbb_key:
        return {"success": False, "error": "IMGBB_API_KEY 미설정 — 이미지 호스팅 필요"}

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    url = "https://api.imgbb.com/1/upload"
    data = {"key": imgbb_key, "image": encoded}
    try:
        res = requests.post(url, data=data, timeout=30)
        if res.status_code == 200:
            img_url = res.json()["data"]["url"]
        else:
            return {"success": False, "error": f"이미지 업로드 실패 ({res.status_code}): {res.text}"}
    except Exception as e:
        return {"success": False, "error": f"이미지 업로드 실패: {e}"}

    # 인스타그램 발행
    post_url, error_msg = upload_image_to_instagram(account_id, access_token, img_url, caption)
    if post_url:
        return {"success": True, "post_url": post_url, "image_url": img_url}
    return {"success": False, "error": error_msg or "Instagram 발행 실패"}


if __name__ == "__main__":
    result = post_to_instagram(
        title="테스트 카드뉴스",
        content="멋쟁이 인사이트 자동화 테스트입니다.",
        caption="📊 멋쟁이 인사이트 테스트\n#주식 #투자 #코스피 #미국주식",
        stars="★★★★★"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
