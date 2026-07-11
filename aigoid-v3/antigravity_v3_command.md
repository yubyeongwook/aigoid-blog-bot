# 안티그라비티 — v3 고도화 시스템 적용 명령어
# 아래 전체를 안티그라비티에 붙여넣으세요

---

다음 작업을 순서대로 실행해줘.

## 작업 1 — 새 파일들 생성

aigoid-blog-bot/trackers/ 폴더 생성 후
trackers/__init__.py 빈 파일 생성
trackers/pick_tracker.py 생성 (받은 파일)
trackers/picks_history.json 빈 파일 생성 ({})

aigoid-blog-bot/agents/ 폴더에 추가:
agents/dart_nlp_agent.py (받은 파일)
agents/foreign_tracker_agent.py (받은 파일)
agents/sentiment_agent.py (받은 파일)
agents/synthesis_agent_v3.py (받은 파일)

루트에 추가:
main_daily_v3.py (받은 파일)

.github/workflows/ 에 추가:
daily_v3.yml (받은 파일)

## 작업 2 — 확인
ls aigoid-blog-bot/trackers/
ls aigoid-blog-bot/agents/

## 작업 3 — 테스트 실행
python main_daily_v3.py

성공 시 이렇게 출력:
[0/7] 전일 픽 성과 업데이트...
[1/7] 시장 데이터 수집...
[2/7] 뉴스·공시 수집...
[3/7] 글로벌 매크로 분석...
[4/7] 수급 + 외국인 종목 추적...
[5/7] 실적·공시 NLP 분석...
[6/7] 기술적 분석 + 감성 지수...
[7/7] 6개 에이전트 통합 판단...
✅ 발행 완료

## 작업 4 — 깃허브 푸시
git add .
git commit -m "v3.0 6개 에이전트 + 픽추적 + 감성지수 고도화"
git push

완료되면 알려줘.
