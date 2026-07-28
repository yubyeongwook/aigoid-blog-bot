import os
import requests
import webbrowser
import sys
import urllib.parse
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    env_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\.env"
    load_dotenv(env_path, override=True)

    # 1. Facebook App Credentials (자동 하드코딩으로 입력 최소화)
    app_id = "2180630959386928"
    app_secret = "0a3d7c4bd24e26f4464c833e33968010"
    redirect_uri = "http://localhost/"
    
    print("====================================================")
    print("     🚀 인스타그램 원클릭 자동 연동 시스템")
    print("====================================================")
    
    # 2. 로그인 URL 생성 및 브라우저 열기
    scopes = ["instagram_basic", "instagram_content_publish", "pages_read_engagement", "pages_show_list", "business_management"]
    scopes_str = ",".join(scopes)
    
    login_url = (
        f"https://www.facebook.com/v20.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"scope={scopes_str}&"
        f"response_type=code"
    )
    
    print("\n브라우저에서 페이스북 연동 로그인 페이지를 엽니다...")
    print("만약 브라우저가 자동으로 열리지 않으면 아래 링크를 복사하여 브라우저에 붙여넣어 주세요:")
    print(login_url)
    print("-" * 50)
    
    webbrowser.open(login_url)
    
    print("\n[안내] 페이스북 로그인을 마친 후 브라우저 주소창에")
    print("'사이트에 연결할 수 없음' 또는 'http://localhost/?code=...'로 시작하는 에러 주소가 나타납니다. (정상입니다!)")
    print("그 주소창의 주소 전체를 복사해서 아래에 붙여넣어 주세요.")
    print("-" * 50)
    
    # 3. 리디렉션된 URL 입력받기
    redirected_input = input("복사한 주소를 입력하세요: ").strip()
    if not redirected_input:
        print("❌ 입력된 주소가 없습니다. 연동을 중단합니다.")
        return
        
    # 4. Code 파라미터 추출
    code = None
    if "code=" in redirected_input:
        try:
            parsed = urllib.parse.urlparse(redirected_input)
            params = urllib.parse.parse_qs(parsed.query)
            code = params.get("code", [None])[0]
        except Exception:
            code = None
            
    if not code:
        # 혹시 code 값만 그대로 넣은 경우 처리
        if redirected_input.startswith("AQ"):
            code = redirected_input
        else:
            print("❌ 올바른 인증 주소(또는 Code)를 찾을 수 없습니다. 다시 시도해 주세요.")
            return

    # 5. 60일 장기 User Access Token으로 교환
    print("\n🔄 [1단계] 60일 장기 액세스 토큰 교환 중...")
    exchange_url = "https://graph.facebook.com/v20.0/oauth/access_token"
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "client_secret": app_secret,
        "code": code
    }
    
    res = requests.get(exchange_url, params=params)
    if res.status_code != 200:
        print(f"❌ 토큰 교환 실패 ({res.status_code}):")
        print(res.text)
        return
        
    long_user_token = res.json().get("access_token")
    print("✅ 장기 User Access Token 발급 성공!")
    print(f"👉 발급된 토큰 (디버깅용): {long_user_token}\n")
    
    # 6. 페이스북 페이지 정보 조회 및 영구 토큰 획득
    print("\n🔄 [2단계] 영구 Page Access Token 조회 중...")
    accounts_url = "https://graph.facebook.com/v20.0/me/accounts"
    res_accounts = requests.get(accounts_url, params={"access_token": long_user_token})
    
    if res_accounts.status_code != 200:
        print(f"❌ 페이지 정보 조회 실패 ({res_accounts.status_code}):")
        print(res_accounts.text)
        return
        
    accounts_data = res_accounts.json().get("data", [])
    if not accounts_data:
        print("❌ 관리하는 페이스북 페이지를 찾을 수 없습니다. 연동 권한 동의 여부를 확인해 주세요.")
        return
        
    # 인스타그램 계정이 연동되어 있는지 조회
    target_page = None
    target_instagram_id = None
    target_page_token = None
    
    print("\n🔄 [3단계] 연결된 인스타그램 비즈니스 계정 검색 중...")
    for page in accounts_data:
        page_id = page.get("id")
        page_token = page.get("access_token")
        page_name = page.get("name")
        
        # 각 페이지별 연결된 인스타그램 비즈니스 계정 조회
        ig_url = f"https://graph.facebook.com/v20.0/{page_id}"
        ig_params = {
            "fields": "instagram_business_account",
            "access_token": page_token
        }
        res_ig = requests.get(ig_url, params=ig_params)
        if res_ig.status_code == 200:
            ig_data = res_ig.json()
            if "instagram_business_account" in ig_data:
                target_page = page_name
                target_page_token = page_token
                target_instagram_id = ig_data["instagram_business_account"]["id"]
                break

    if not target_instagram_id:
        print("\n⚠️ 페이스북 페이지는 찾았으나, 연결된 인스타그램 비즈니스 계정을 찾을 수 없습니다.")
        print("임시로 첫 번째 페이지의 영구 토큰으로 세팅을 계속 진행합니다.")
        target_page = accounts_data[0].get("name")
        target_page_token = accounts_data[0].get("access_token")
        target_instagram_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
        
    print(f"\n✅ 매칭된 페이스북 페이지: {target_page}")
    print(f"✅ 매칭된 인스타그램 계정 ID: {target_instagram_id}")
    
    # 7. .env 파일 자동 업데이트
    if not os.path.exists(env_path):
        print("❌ .env 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        return
        
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    new_lines = []
    updated_token = False
    updated_ig_id = False
    
    for line in lines:
        if line.startswith("META_ACCESS_TOKEN="):
            new_lines.append(f"META_ACCESS_TOKEN={target_page_token}\n")
            updated_token = True
        elif line.startswith("INSTAGRAM_ACCOUNT_ID=") and target_instagram_id:
            new_lines.append(f"INSTAGRAM_ACCOUNT_ID={target_instagram_id}\n")
            updated_ig_id = True
        else:
            new_lines.append(line)
            
    if not updated_token:
        new_lines.append(f"META_ACCESS_TOKEN={target_page_token}\n")
    if not updated_ig_id and target_instagram_id:
        new_lines.append(f"INSTAGRAM_ACCOUNT_ID={target_instagram_id}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    print("\n====================================================")
    print("🎉 인스타그램 연동 및 영구 토큰 발급 성공!")
    print("   .env 파일에 토큰 정보가 자동으로 업데이트되었습니다.")
    print("====================================================")

if __name__ == "__main__":
    main()
