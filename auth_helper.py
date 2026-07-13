"""
auth_helper.py — Blogger API OAuth 2.0 인증 헬퍼
사용자가 직접 브라우저에서 인증한 뒤 발급받은 코드를 통해 refresh_token을 획득하고 .env를 업데이트합니다.
"""
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import requests
import urllib.parse
from dotenv import load_dotenv

def main():
    env_path = ".env"
    load_dotenv(env_path)
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ 오류: .env 파일에 GOOGLE_CLIENT_ID 또는 GOOGLE_CLIENT_SECRET이 정의되어 있지 않습니다.")
        return
        
    redirect_uri = "http://localhost"
    
    # 1. 인증 URL 생성
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        # Blogger API 및 YouTube 동영상 업로드(v4.5 쇼츠) 권한을 동시에 획득합니다.
        "scope": "https://www.googleapis.com/auth/blogger https://www.googleapis.com/auth/youtube.upload",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    
    print("=" * 80)
    print(" 🔑 Blogger API OAuth 인증 도우미")
    print("=" * 80)
    print("1. 아래의 URL을 웹 브라우저 주소창에 복사해서 이동한 뒤 Google 로그인을 완료해주세요:")
    print("\n   " + auth_url + "\n")
    print("2. 로그인이 완료되면 브라우저 주소창이 다음과 같이 변경됩니다:")
    print("   http://localhost/?code=4/0AdQt8q...&scope=...")
    print("3. 주소창의 전체 URL 또는 code= 뒷부분의 코드만 복사해서 아래에 입력해주세요.")
    print("=" * 80)
    
    code_input = input("주소창 URL 또는 인증 코드를 입력하세요: ").strip()
    if not code_input:
        print("❌ 입력값이 없어 종료합니다.")
        return
        
    code = code_input
    if "code=" in code_input:
        # URL에서 code 파라미터 추출
        parsed = urllib.parse.urlparse(code_input)
        queries = urllib.parse.parse_qs(parsed.query)
        if "code" in queries:
            code = queries["code"][0]
            
    print(f"\n[정보] 추출된 인증 코드: {code[:15]}...")
    
    # 2. 토큰 교환 요청
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    print("\nGoogle 서버와 토큰 교환 중...")
    res = requests.post(token_url, data=data)
    if res.status_code != 200:
        print(f"❌ 토큰 교환 실패 (상태 코드: {res.status_code})")
        print(res.text)
        return
        
    tokens = res.json()
    refresh_token = tokens.get("refresh_token")
    access_token = tokens.get("access_token")
    
    if not refresh_token:
        print("\n⚠️ 경고: refresh_token이 수신되지 않았습니다.")
        print("이미 이전에 앱을 승인한 상태일 수 있습니다.")
        print("해결법: 구글 계정 보안 설정에서 해당 앱의 접근 권한을 삭제(연결 해제)한 뒤 이 스크립트를 다시 실행하여 처음부터 다시 동의(consent)해 주셔야 합니다.")
        
    print("\n✅ 토큰을 성공적으로 가져왔습니다!")
    
    # 3. .env 파일 업데이트
    if not os.path.exists(env_path):
        print(f"❌ {env_path} 파일이 존재하지 않습니다.")
        return
        
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    new_lines = []
    updated_refresh = False
    updated_access = False
    
    for line in lines:
        if line.startswith("GOOGLE_REFRESH_TOKEN=") and refresh_token:
            new_lines.append(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
            updated_refresh = True
        elif line.startswith("GOOGLE_ACCESS_TOKEN=") and access_token:
            new_lines.append(f"GOOGLE_ACCESS_TOKEN={access_token}\n")
            updated_access = True
        else:
            new_lines.append(line)
            
    if not updated_refresh and refresh_token:
        new_lines.append(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
    if not updated_access and access_token:
        new_lines.append(f"GOOGLE_ACCESS_TOKEN={access_token}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    print("\n💾 .env 파일의 토큰 정보가 성공적으로 업데이트되었습니다!")

if __name__ == "__main__":
    main()
