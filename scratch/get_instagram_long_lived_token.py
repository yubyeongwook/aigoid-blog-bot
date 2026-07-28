import os
import requests
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    print("====================================================")
    print("      Instagram 영구 토큰 발급 헬퍼 스크립트")
    print("====================================================")
    
    app_id = input("1. 페이스북 App ID를 입력하세요: ").strip()
    app_secret = input("2. 페이스북 App Secret을 입력하세요: ").strip()
    short_token = input("3. Graph API Explorer 임시 토큰을 입력하세요: ").strip()
    
    if not app_id or not app_secret or not short_token:
        print("❌ 모든 입력값은 필수입니다.")
        return

    # 1. 60일 장기 토큰으로 변환
    print("\n🔄 [1단계] 60일 장기 User Access Token 요청 중...")
    exchange_url = "https://graph.facebook.com/v20.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    }
    
    res = requests.get(exchange_url, params=params)
    if res.status_code != 200:
        print(f"❌ 장기 토큰 교환 실패 ({res.status_code}):")
        print(res.text)
        return
        
    long_user_token = res.json().get("access_token")
    print("✅ 장기 User Access Token 발급 성공!")
    
    # 2. 영구 Page Access Token 요청
    print("\n🔄 [2단계] 영구 Page Access Token 및 연동 정보 조회 중...")
    accounts_url = "https://graph.facebook.com/v20.0/me/accounts"
    params_accounts = {
        "access_token": long_user_token
    }
    
    res_accounts = requests.get(accounts_url, params=params_accounts)
    if res_accounts.status_code != 200:
        print(f"❌ 페이지 정보 조회 실패 ({res_accounts.status_code}):")
        print(res_accounts.text)
        return
        
    accounts_data = res_accounts.json().get("data", [])
    if not accounts_data:
        print("❌ 관리하는 페이스북 페이지가 없습니다. 인스타그램과 연동된 페이지의 관리자 계정인지 확인해 주세요.")
        return
        
    print("\n====================================================")
    print("🎉 영구 페이지 액세스 토큰 조회 완료!")
    print("아래 리스트에서 인스타그램과 연동된 페이지의 토큰을 복사하여 .env에 입력하세요.")
    print("====================================================\n")
    
    for idx, page in enumerate(accounts_data):
        print(f"[{idx+1}] 페이지 이름: {page.get('name')}")
        print(f"    페이지 ID: {page.get('id')}")
        print(f"    🔑 영구 토큰 (META_ACCESS_TOKEN):")
        print(f"    {page.get('access_token')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
