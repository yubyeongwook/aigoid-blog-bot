# 멋쟁이 인사이트 자동화 시스템

## 구조
```
collectors/
  market_collector.py   — pykrx + KIS API 시장 데이터
  news_collector.py     — 네이버뉴스 + DART 공시
generators/
  report_generator.py   — Claude API 리포트 생성
publishers/
  blogger_publisher.py  — Blogger 자동 발행
main_daily.py           — 매일 오전 7시 자동 실행
main_weekly.py          — 매주 일요일 자동 실행
.github/workflows/
  daily.yml             — 일일 액션
  weekly.yml            — 주간 액션
```

## 설치
```
pip install -r requirements.txt
```

## .env 설정
```
ANTHROPIC_API_KEY=
KIS_APP_KEY=
KIS_APP_SECRET=
DART_API_KEY=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
BLOG_ID=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
```

## 수동 실행
```
python main_daily.py   # 일일 리포트
python main_weekly.py  # 주간 결산
```

## 자동 실행
깃허브 Actions가 매일 오전 7시, 매주 일요일 오전 9시 자동 실행
