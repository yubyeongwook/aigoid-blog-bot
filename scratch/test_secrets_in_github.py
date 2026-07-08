import os, requests

def test_gemini():
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        return "❌ GEMINI_API_KEY가 설정되지 않았습니다."
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        body = {"contents": [{"parts": [{"text": "Hello"}]}]}
        res = requests.post(url, json=body, timeout=10)
        if res.status_code == 200:
            return "✅ Gemini API 연결 성공"
        else:
            return f"❌ Gemini API 오류 (상태코드 {res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ Gemini API 예외 발생: {e}"

def test_anthropic():
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return "⚠️ ANTHROPIC_API_KEY가 설정되지 않았습니다. (선택사항)"
    try:
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        body = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        res = requests.post("https://api.anthropic.com/v1/messages", json=body, headers=headers, timeout=10)
        if res.status_code == 200:
            return "✅ Anthropic API 연결 성공"
        else:
            return f"❌ Anthropic API 오류 (상태코드 {res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ Anthropic API 예외 발생: {e}"

def test_google_oauth():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "")
    
    missing = []
    if not client_id: missing.append("GOOGLE_CLIENT_ID")
    if not client_secret: missing.append("GOOGLE_CLIENT_SECRET")
    if not refresh_token: missing.append("GOOGLE_REFRESH_TOKEN")
    
    if missing:
        return f"❌ 구글 OAuth 변수 누락: {', '.join(missing)}"
        
    try:
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        res = requests.post(url, data=data, timeout=10)
        if res.status_code == 200:
            return "✅ 구글 OAuth 토큰 갱신 성공"
        else:
            return f"❌ 구글 OAuth 오류 (상태코드 {res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ 구글 OAuth 예외 발생: {e}"

def test_naver():
    client_id = os.getenv("NAVER_CLIENT_ID", "")
    client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return "❌ 네이버 API 변수 누락"
    try:
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
        url = "https://openapi.naver.com/v1/search/news.json?query=주식&display=1"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return "✅ 네이버 API 연결 성공"
        else:
            return f"❌ 네이버 API 오류 (상태코드 {res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ 네이버 API 예외 발생: {e}"

def test_dart():
    key = os.getenv("DART_API_KEY", "")
    if not key:
        return "❌ DART_API_KEY 누락"
    try:
        url = f"https://opendart.fss.or.kr/api/disclosureToday.json?crtfc_key={key}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return "✅ DART API 연결 성공"
        else:
            return f"❌ DART API 오류 (상태코드 {res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ DART API 예외 발생: {e}"

def main():
    print("=" * 50)
    print(" 깃허브 Actions Secrets 검증 테스트")
    print("=" * 50)
    print(test_gemini())
    print(test_anthropic())
    print(test_google_oauth())
    print(test_naver())
    print(test_dart())
    print("=" * 50)

if __name__ == "__main__":
    main()
