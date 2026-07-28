import requests
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    token = input("페이스북 액세스 토큰을 입력하세요: ").strip()
    if not token:
        print("토큰이 비어있습니다.")
        return
        
    # Get current user profile
    params = {"access_token": token}
    res_me = requests.get("https://graph.facebook.com/v20.0/me", params=params)
    if res_me.status_code == 200:
        me_data = res_me.json()
        print(f"\n👤 로그인된 페이스북 계정: {me_data.get('name')} (ID: {me_data.get('id')})")
    else:
        print("사용자 정보 조회 실패:", res_me.text)
        
    url = "https://graph.facebook.com/v20.0/me/accounts"
    
    print("\n🔄 페이지 정보 조회 중...")
    res = requests.get(url, params=params)
    print("Status Code:", res.status_code)
    
    if res.status_code == 200:
        data = res.json().get("data", [])
        if not data:
            print("⚠️ 관리하는 페이스북 페이지가 없습니다.")
            # Let's inspect the token permissions using /me/permissions
            print("\n🔄 토큰 권한 목록 조회 중...")
            res_perm = requests.get("https://graph.facebook.com/v20.0/me/permissions", params=params)
            if res_perm.status_code == 200:
                print("현재 토큰의 권한 상태:")
                for p in res_perm.json().get("data", []):
                    print(f"  - {p.get('permission')}: {p.get('status')}")
            else:
                print("권한 조회 실패:", res_perm.text)
        else:
            print("\n🎉 페이지 조회 성공!")
            for p in data:
                print(f"페이지 이름: {p.get('name')}")
                print(f"페이지 ID: {p.get('id')}")
                print(f"페이지 토큰: {p.get('access_token')}")
                print("-" * 50)
    else:
        print("페이지 조회 실패:")
        print(res.text)

if __name__ == "__main__":
    main()
