import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YouTube 업로드 권한을 포함하는 Google OAuth Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    """기존 Blogger용 Google OAuth Credential 정보를 재사용하여 YouTube 서비스 객체를 갱신(Refresh)하고 로드합니다."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "")
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN", "")

    if not client_id or not client_secret or not refresh_token:
        print("⚠️ 유튜브 배포 에이전트: 구글 API 연동 정보가 부족합니다.")
        return None

    try:
        # 기존 OAuth 토큰 연동 및 자동 갱신 설정
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES
        )
        
        # 만료되었을 경우 갱신 시도
        if creds and creds.expired and creds.refresh_token:
            print("🔄 유튜브 배포 에이전트: OAuth Access Token 갱신 중...")
            creds.refresh(Request())
            
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"⚠️ 유튜브 API 서비스 빌드 중 에러: {e}")
        return None

def upload_shorts_to_youtube(video_path: str, title: str, description: str) -> bool:
    """생성된 MP4 쇼츠 영상을 사용자의 유튜브 채널에 비공개(private) 또는 공개로 자동 업로드합니다."""
    print("\n[Publisher Agent] 유튜브 쇼츠 자동 업로드 단계 진입...")
    
    if not os.path.exists(video_path):
        print(f"에러: 업로드할 쇼츠 영상 파일이 경로에 없습니다: {video_path}")
        return False
        
    youtube = get_youtube_service()
    if not youtube:
        print("⚠️ 유튜브 API 연동이 승인되지 않아 업로드를 스킵합니다.")
        return False
        
    # 유튜브 쇼츠 필수 조건: 제목에 #Shorts 포함
    shorts_title = title
    if "#Shorts" not in title and "#shorts" not in title:
        shorts_title = f"{title} #Shorts"
        
    # 유튜브 API 업로드 메타데이터 정의
    body = {
        "snippet": {
            "title": shorts_title[:100], # 최대 100자
            "description": description[:5000],
            "tags": ["Shorts", "주식", "멋쟁이인사이트", "재테크"],
            "categoryId": "24" # Entertainment 카테고리 (혹은 25: News & Politics)
        },
        "status": {
            # 안전을 위해 최초 업로드 시에는 'unlisted'(일부공개) 또는 'private'(비공개)로 올리고 
            # 사용자가 대시보드에서 직접 체크 후 전환할 수 있도록 지원합니다.
            "privacyStatus": "unlisted"
        }
    }
    
    try:
        print(f"📤 유튜브 업로드 중: '{shorts_title}' (파일 크기: {os.path.getsize(video_path) / (1024*1024):.2f} MB)")
        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            chunksize=1024 * 1024, # 1MB 청크 단위 업로드
            resumable=True
        )
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   업로드 진행률: {int(status.progress() * 100)}%")
                
        video_id = response.get("id", "")
        print(f"✅ 유튜브 쇼츠 업로드 성공! 비디오 ID: {video_id}")
        print(f"🔗 유튜브 영상 주소: https://youtu.be/{video_id}")
        return True
    except Exception as e:
        print(f"유튜브 쇼츠 업로드 중 예외 발생: {e}")
        return False
