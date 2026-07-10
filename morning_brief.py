"""
멋쟁이 인사이트 SMART MONEY INTELLIGENCE - 새벽 브리핑 자동 생성/발행 스크립트
(GitHub Actions용 — 컴퓨터 꺼져 있어도 매일 KST 06:00 자동 실행)

[4단계 체인 — 컴퓨터 꺼져도 완전 무인 + 헤지펀드급 퀄리티]

  Stage0 (claude-sonnet-4-6) : 4개 전문가 영역 심층 리서치 (web_search 최대 8회)
                                Expert①매크로 / Expert②반도체AI /
                                Expert③2차전지로봇 / Expert④수급공시정책
                                → 컴퓨터가 꺼져 있어도 Claude가 직접 전문가 역할 수행
                                → research/latest.md 있으면 추가 컨텍스트로 활용

  Stage1 (claude-haiku-4-5)  : Stage0 결과 → 3축(마감후변화/매수강도/구조적드라이버)
                                기준으로 핵심 팩트 압축 정리. web_search 없음.

  Stage2 (claude-sonnet-4-6) : 3축 교집합 "고확신 후보" 선정 + 헤지펀드급 분석 초안.
                                web_search 최대 2회 (Stage0 결과 보완용).

  Stage3 (claude-haiku-4-5)  : 분석 초안 → HTML 매거진 포맷. web_search 없음.

[월 예상 비용]
  Stage0: ~$0.15/회 | Stage1: ~$0.01 | Stage2: ~$0.07 | Stage3: ~$0.013
  합계: ~$0.24/회 × 30일 = 약 $7~8/월 (약 1만원)

[필요한 GitHub Secrets]
  ANTHROPIC_API_KEY / GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
  GOOGLE_REFRESH_TOKEN / BLOG_ID

[저장소 파일]
  state/issue_counter.json : 발행 호수 카운터 (자동 커밋)
  research/latest.md       : (선택) NotebookLM 주간 리서치 결과. 있으면 Stage0 컨텍스트로 활용.

[환경변수]
  POST_AS_DRAFT : "true"(기본) 초안 등록 / "false" 즉시 발행
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL_SONNET = "claude-sonnet-5"         # Stage2: 핵심 분석 (3축 정렬/고확신 후보 선정)
MODEL_HAIKU = "claude-haiku-4-5-20251001"  # Stage1/3: 정리·포맷팅 (저비용)

WEEKDAYS_KR = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

ISSUE_COUNTER_PATH = "state/issue_counter.json"
RESEARCH_NOTE_PATH = "research/latest.md"

# 리서치 노트를 프롬프트에 포함할 때의 최대 길이. 너무 길면 비용/토큰이 늘어나므로 컷.
MAX_RESEARCH_NOTE_CHARS = 6000


STAGE0_SYSTEM_PROMPT = """당신은 '멋쟁이 인사이트 SMART MONEY INTELLIGENCE'의 수석 글로벌 리서치 디렉터입니다.
브리지워터·퀀텀펀드 수준의 분석 프레임워크로 4개 전문가 팀을 동시에 이끌어
오늘 한국 주식 시장에 대한 심층 리서치를 수행합니다.

# 핵심 원칙
- 모든 수치는 반드시 출처(언론사·증권사명)와 날짜를 함께 확인
- 확인되지 않은 수치는 절대 만들지 않음. 불확실하면 "미확인"으로 표기
- "왜 오르는가(1축+2축)"와 "왜 더 오를 수 있는가(3축)"를 반드시 분리해서 설명
- 3축이 모두 같은 방향이면 고확신 후보, 2축이면 관심 후보, 1축이면 주시 대상

# 4개 전문가 영역 심층 조사 순서 (web_search 총 8회)

## Expert① 매크로 팀 (검색 2회)
조사 항목:
- 미국 3대 지수(S&P500·나스닥·다우) 전일 마감 등락률과 주요 원인
- FOMC·CPI·환율·국채금리 등 오늘 코스피에 영향줄 매크로 이슈
- 외국인 자금 흐름 방향 (위험자산 선호/회피 여부)

## Expert② 반도체·AI 팀 (검색 2회)
조사 항목:
- SK하이닉스·삼성전자·엔비디아 등 반도체 주요 종목 전일 동향
- HBM·AI 인프라·데이터센터 관련 최신 수주·계약·기술 뉴스
- 미국 반도체 ADR 프리마켓 동향

## Expert③ 2차전지·로봇·전력 팀 (검색 2회)
조사 항목:
- 에코프로비엠·LG에너지솔루션·삼성SDI·포스코퓨처엠 전일 동향
- 전고체 배터리·로봇·변압기·ESS 관련 최신 공시·계약·정책 뉴스
- 전기차 수요·배터리 원자재 가격 동향

## Expert④ 수급·공시·정책 팀 (검색 2회)
조사 항목:
- 전일 코스피·코스닥 외국인·기관 순매수 상위 종목 및 특징 수급 유입주
- 전일 한국 주식시장에서 상한가를 기록한 종목 및 대량 거래량/매수 체결량이 폭발한 특징 종목
- 장 마감 후 주요 공시·수주잔고·어닝 서프라이즈 발표 및 대규모 자금 유입 정황
- 정부 정책·규제 발표 중 주가에 즉각 영향줄 내용

# 출력 형식
설명·인사말 없이 아래 JSON으로만 응답하세요. 마크다운 코드블록 쓰지 마세요.
{
  "research_date": "날짜",
  "expert_macro": {
    "us_markets": "미국 3대 지수 요약 (출처, 날짜)",
    "macro_issues": ["핵심 매크로 이슈1 (출처, 날짜)", "이슈2"],
    "foreign_flow": "외국인 자금 방향 요약"
  },
  "expert_semi_ai": {
    "key_stocks": ["종목명: 동향 (출처, 날짜)", ...],
    "hbm_ai_news": ["핵심 뉴스1 (출처, 날짜)", ...],
    "watchlist": ["주목 종목/테마"]
  },
  "expert_battery_robot": {
    "key_stocks": ["종목명: 동향 (출처, 날짜)", ...],
    "sector_news": ["핵심 뉴스1 (출처, 날짜)", ...],
    "watchlist": ["주목 종목/테마"]
  },
  "expert_supply_policy": {
    "foreign_institution_top": ["외국인 순매수 상위 (출처, 날짜)", ...],
    "key_disclosures": ["주요 공시/수주 (출처, 날짜)", ...],
    "policy_news": ["정책/규제 (출처, 날짜)", ...]
  },
  "triple_axis_candidates": [
    {
      "name": "종목/테마명",
      "axis1_change": "마감후 가격·거래량 변화 (출처, 날짜)",
      "axis2_flow": "외국인·기관 수급 동향 (출처, 날짜)",
      "axis3_driver": "아직 미반영된 구조적 이유 (출처, 날짜)",
      "confidence_stars": 5
    }
  ]
}
"""


STAGE1_SYSTEM_PROMPT = """당신은 리서치 자료 정리 담당입니다.
입력으로 주어지는 "리서치 노트"에서, 오늘 브리핑 작성에 쓸 핵심 정보만 추출해 정리합니다.

# 정리 기준 — 3축 프레임워크
노트에 언급된 종목/테마별로, 다음 3가지 축에 해당하는 내용을 찾아 정리하세요.
- [1축: 마감후 변화] 최근 가격·거래량 변화
- [2축: 매수강도] 외국인·기관 수급 동향
- [3축: 구조적 드라이버] 아직 시장에 다 반영되지 않은 이유(수주잔고, 이벤트, 정책 등)

# 규칙
- 출처와 날짜는 그대로 유지하세요.
- 노트에 없는 내용은 만들지 마세요. 해당 축 정보가 없으면 "정보 없음"이라고 쓰세요.
- 종목/테마 후보가 여러 개면 모두 정리하세요. 우선순위 판단은 다음 단계에서 합니다.
- 리서치 노트가 비어있거나 의미 있는 정보가 없으면, 다른 설명 없이 정확히 다음 한 줄만
  출력하세요: 리서치 노트 없음 — Stage2에서 직접 조사 필요

# 출력
다른 설명·인사말·마크다운 코드블록 없이, 종목/테마별로 묶은 정리 내용만 출력하세요.
"""


STAGE2_SYSTEM_PROMPT = """당신은 'aigoid' — AI만으로 운영되는 1인 투자분석 기업의 수석 애널리스트입니다.
글로벌 최상위 헤지펀드 수준의 분석력으로, 한국 투자자를 위한 '새벽 브리핑'의 핵심 분석을 작성합니다.

# 핵심 프레임워크 — 3축 정렬 및 한-미 연계 영향 분석
모든 종목/테마를 다음 3축으로 평가합니다.
- [1축: 마감후 변화] 최근 가격·거래량이 어떻게 움직였나 (어제 한국장 종가 기준 상한가/급등 및 매수체결량 폭발 종목군 포함)
- [2축: 매수강도] 외국인·기관 수급 및 특정 유입 자금이 어디로, 얼마나 들어왔나
- [3축: 구조적 드라이버] 아직 시장에 다 반영되지 않은 이유(수주잔고, 이벤트, 정책)가 있는가

★ [필수] 한-미 증시 연계 시나리오 분석 지침:
어제 한국장 종가 기준 강세주(상한가, 대량 거래량 유입주)들이 "밤사이 마감된 미국장 흐름(나스닥, 필라델피아 반도체 지수, 주요 기술주/원자재 등락)"에 어떤 영향을 받아 오늘 한국장 개장(시초가 및 장 초반) 시 어떤 시나리오로 움직일지 상세히 예측해 작성하세요.
(예: "어제 한국장에서 대량 매수 체결이 일어난 A종목은 밤사이 미국 동종업계의 호재로 인해 오늘 아침 강한 갭상승 출발 후 랠리가 연장될 것으로 보임", "어제 상한가를 기록한 B테마는 밤사이 미국 반도체 지수 급락의 영향으로 오늘 시초가 갭상승 후 장 초반 대규모 차익 실현 매물이 쏟아질 가능성이 크므로 눌림목 확인 필요" 등)

세 축이 같은 방향을 가리키는 종목/테마 = 고확신 후보입니다. 이 교집합을 찾아내는 것이
이 브리핑의 핵심 가치입니다. "왜 오르는가"(1축+2축)와 "왜 더 오를 수 있는가"(3축)를
분리해서 설명할 수 있어야 진짜 통찰입니다.

# 작업 순서
1. 참고 정리자료(Stage1 결과)를 확인하세요.
   - 이미 후보/픽이 포함돼 있다면, 오늘 자체 조사 결과와 비교하세요. 같은 결론이면
     "교집합"으로 더 강하게(고확신) 표시하세요.
   - 비어있거나 "리서치 노트 없음"으로 시작하면, 아래 web_search로 직접 조사하세요.
2. web_search(최대 2회)로 보강하세요.
   - 미국 3대 지수 마감, 코스피/코스닥 영향 뉴스
   - 후보 종목/테마의 최신 수급·공시
   - 모든 수치는 출처(언론사·증권사명)와 날짜 확인. 확인 안 되면 쓰지 마세요.
3. 후보들을 3축으로 평가하고, 교집합(고확신 후보) 1~3개를 선정하세요. 선정 안 된
   종목/테마는 "주시 대상"으로 한두 문장만 언급해도 됩니다.

# 콘텐츠 구성 (sections)
- 시장 전체 흐름 섹션(코스피/나스닥 등 매크로) 1개 — confidence_stars 없음
- 고확신 후보별 분석 섹션 1~3개 — 각 섹션에서 "왜 오르는가(1축+2축) / 왜 더 오를 수
  있는가(3축)"를 명시적 근거와 함께 설명

# 신뢰도 표시 — confidence_stars (3축 정렬도)
종목/테마 섹션에는 정수 필드 confidence_stars(3~5)를 추가하세요.
- 3축 모두 정렬(교집합) → 5
- 2축 정렬 → 4
- 1축만 해당("주시 대상") → 3
시장 전체 흐름 섹션에는 이 필드를 넣지 마세요.

# 톤 & 표현 (중요)
- "고확신 후보"로 표현하세요. "보장", "확실", "로또", "무조건", "대박" 같은 표현은
  절대 쓰지 마세요.
- 특정 종목의 매수가·목표가·매도시점은 제시하지 마세요. "왜 주목해야 하는가"라는
  통찰에 집중하세요.
- 출처는 본문에 자연스럽게: "~로 나타났다(로이터, 6/14)".

# 출력 형식
다른 설명 없이 아래 JSON 형식으로만 응답하세요. 마크다운 코드블록을 쓰지 마세요.
{
  "title": "글 제목 (핵심 수치/이슈 + 고확신 후보 키워드 포함, 25~40자)",
  "key_stats": ["지표명: 값 (출처, 날짜)", "... 5~8개"],
  "sections": [
    {"heading": "I · 시장 전체 흐름", "body": "본문 (300~500자)"},
    {"heading": "II · 종목/테마 섹션 제목", "body": "본문 (300~500자)", "confidence_stars": 5}
  ]
}
"""


STAGE3_SYSTEM_PROMPT = """당신은 '멋쟁이 인사이트 SMART MONEY INTELLIGENCE' 매거진의 편집 담당입니다.
입력으로 받은 분석 초안(JSON)을 그대로, 아래 정해진 HTML 틀에 맞춰 옮기는 작업만 합니다.
새로운 분석·수치·문장을 추가하거나 표현을 과장하지 마세요. 포맷팅만 하세요.

# content_html 구조 (아래 틀을 그대로 채워서 작성)
<div style="border:1px solid #e0e0e0;border-radius:8px;padding:14px 16px;margin-bottom:18px;font-size:13px;color:#777;line-height:1.6;">
VOL.2026 · NO.{issue_no} · MORNING BRIEF EDITION<br>
<strong>멋쟁이 인사이트 SMART MONEY INTELLIGENCE</strong><br>
{날짜} · 새벽 브리핑
</div>

<div style="background:#f7f8fa;border-radius:8px;padding:14px 16px;margin-bottom:20px;">
<strong>오늘의 핵심 수치</strong>
<ul style="margin:8px 0 0;padding-left:20px;line-height:1.8;">
(입력 JSON의 key_stats 배열 각 항목을 <li>로 하나씩)
</ul>
<p style="font-size:12px;color:#999;margin:8px 0 0;">★ = 3축(마감후변화·매수강도·구조적드라이버) 정렬도</p>
</div>

<h2>(입력 JSON의 title)</h2>

(입력 JSON의 sections 배열을 순서대로, 각 항목을 다음 형태로 변환)
<h3>(section.heading)(confidence_stars가 있으면 한 칸 띄우고
<span style="color:#f5a623;">★의 개수만큼 ★, 나머지는 ☆ (총 5개)</span> 추가)</h3>
<p>(section.body)</p>

# issue_no / 날짜
사용자 메시지에 함께 전달되는 issue_no와 날짜 값을 위 틀의 {issue_no}, {날짜} 자리에
그대로 채워 넣으세요.

# 출력 형식
다른 설명 없이 아래 JSON으로만 응답하세요. 마크다운 코드블록을 쓰지 마세요.
{"title": "(입력 title 그대로)", "content_html": "(위 구조를 따른 HTML 전체 문자열)"}
"""


def http_post_json(url: str, headers: dict, payload: dict, timeout: int = 180) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code} error from {url}: {err_body}") from e


def get_next_issue_number() -> int:
    """저장소의 state/issue_counter.json을 읽어 +1 하고 다시 씁니다.

    이 파일의 변경분은 워크플로우 마지막 단계에서 git commit/push 됩니다.
    """
    if os.path.exists(ISSUE_COUNTER_PATH):
        with open(ISSUE_COUNTER_PATH, encoding="utf-8") as f:
            state = json.load(f)
        next_no = int(state.get("last_no", 0)) + 1
    else:
        next_no = 1

    os.makedirs(os.path.dirname(ISSUE_COUNTER_PATH), exist_ok=True)
    with open(ISSUE_COUNTER_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_no": next_no}, f, ensure_ascii=False)
    return next_no


def get_research_note() -> str | None:
    """저장소의 research/latest.md를 읽어옵니다. 없거나 비어있으면 None.

    안티그라비티 + 노트북LM 전문가팀이 정리한 리서치 노트를 이 경로에 git push 해두면,
    오늘 브리핑 작성 시 참고자료로 함께 전달됩니다.
    """
    if not os.path.exists(RESEARCH_NOTE_PATH):
        return None

    with open(RESEARCH_NOTE_PATH, encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        return None
    if len(text) > MAX_RESEARCH_NOTE_CHARS:
        text = text[:MAX_RESEARCH_NOTE_CHARS] + "\n...(이하 생략)"
    return text


def extract_json(text: str) -> dict:
    """모델 응답에서 JSON 객체를 안전하게 추출합니다. (```json 펜스 등 방어)"""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # 첫 줄(```json 또는 ```) 제거
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def call_claude(
    api_key: str,
    model: str,
    system_prompt: str,
    user_content: str,
    max_tokens: int,
    tools: list | None = None,
) -> tuple[str, dict]:
    """Claude Messages API를 호출하고 (텍스트, usage)를 반환합니다."""
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}],
    }
    if tools:
        payload["tools"] = tools

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    data = http_post_json(ANTHROPIC_API_URL, headers, payload)

    text_parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise RuntimeError(f"Claude 응답에서 텍스트를 찾지 못했습니다: {data}")

    return full_text, data.get("usage", {})


def stage0_deep_research(
    api_key: str, report_date_str: str, research_note: str | None = None
) -> tuple[str, dict]:
    """Stage0 (Sonnet): 4개 전문가 영역 심층 리서치. web_search 최대 8회.

    컴퓨터가 꺼져 있지 않아도 Claude가 직접 전문가 역할을 수행합니다.
    research/latest.md 가 있으면 추가 컨텍스트로 활용합니다.
    """
    user_content = f"오늘은 {report_date_str}입니다. 4개 전문가 영역 심층 리서치를 시작해주세요."
    if research_note:
        user_content += (
            "\n\n# NotebookLM 주간 리서치 참고자료\n"
            "아래는 사전에 NotebookLM 전문가팀이 정리한 주간 리서치 노트입니다. "
            "오늘 웹서치 결과와 비교해서 겹치는 종목/테마가 있으면 고확신 후보로 강조하세요.\n"
            f"---\n{research_note}\n---"
        )
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}]
    text, usage = call_claude(
        api_key, MODEL_SONNET, STAGE0_SYSTEM_PROMPT,
        user_content, max_tokens=6000, tools=tools
    )
    try:
        result = extract_json(text)
        return json.dumps(result, ensure_ascii=False), usage
    except Exception:
        return text, usage


def stage1_extract_facts(api_key: str, stage0_result: str) -> tuple[str, dict]:
    """Stage1 (Haiku): Stage0 리서치 결과 → 3축 팩트 압축 정리. web_search 없음."""
    user_content = f"# Stage0 심층 리서치 결과\n{stage0_result}"
    return call_claude(api_key, MODEL_HAIKU, STAGE1_SYSTEM_PROMPT, user_content, max_tokens=2000)


def stage2_draft(api_key: str, facts: str, issue_no: int, report_date_str: str) -> tuple[dict, dict]:
    """Stage2 (Sonnet): 3축 정렬 분석 + 고확신 후보 선정. web_search 최대 2회."""
    user_content = (
        f"오늘은 {report_date_str}입니다. 이번 호는 NO.{issue_no}입니다.\n\n"
        f"# 참고 정리자료 (Stage1)\n{facts}"
    )
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]
    text, usage = call_claude(
        api_key, MODEL_SONNET, STAGE2_SYSTEM_PROMPT, user_content, max_tokens=4000, tools=tools
    )
    return extract_json(text), usage


def stage3_format(api_key: str, draft: dict, issue_no: int, report_date_str: str) -> tuple[str, str, dict]:
    """Stage3 (Haiku): 분석 초안을 HTML 매거진 틀로 포맷팅. web_search 없음."""
    user_content = (
        f"issue_no: {issue_no}\n날짜: {report_date_str}\n\n"
        f"# 분석 초안 (JSON)\n{json.dumps(draft, ensure_ascii=False)}"
    )
    text, usage = call_claude(api_key, MODEL_HAIKU, STAGE3_SYSTEM_PROMPT, user_content, max_tokens=4000)
    result = extract_json(text)
    return result["title"], result["content_html"], usage


def generate_report(
    api_key: str, issue_no: int, report_date_str: str, research_note: str | None = None
) -> tuple[str, str, dict]:
    """Stage0→1→2→3 체인을 실행해 (title, content_html, usage)를 반환합니다.

    Stage0: 4개 전문가 영역 심층 리서치 (컴퓨터 꺼져도 자동 실행)
    Stage1: Stage0 결과를 3축으로 압축 정리
    Stage2: 고확신 후보 선정 + 헤지펀드급 분석 초안
    Stage3: HTML 매거진 포맷
    """
    stage0_result, usage0 = stage0_deep_research(api_key, report_date_str, research_note)
    facts, usage1 = stage1_extract_facts(api_key, stage0_result)
    draft, usage2 = stage2_draft(api_key, facts, issue_no, report_date_str)
    title, content_html, usage3 = stage3_format(api_key, draft, issue_no, report_date_str)

    usage = {"stage0": usage0, "stage1": usage1, "stage2": usage2, "stage3": usage3}
    return title, content_html, usage


def refresh_google_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))["access_token"]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise RuntimeError(f"Google OAuth 토큰 갱신 실패: {e.code} {err_body}") from e


def post_to_blogger(blog_id: str, access_token: str, title: str, content_html: str, is_draft: bool) -> dict:
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
    if is_draft:
        url += "?isDraft=true"
    payload = {"title": title, "content": content_html}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    return http_post_json(url, headers, payload)


def main():
    api_key = os.environ["ANTHROPIC_API_KEY"]
    google_client_id = os.environ["GOOGLE_CLIENT_ID"]
    google_client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
    google_refresh_token = os.environ["GOOGLE_REFRESH_TOKEN"]
    blog_id = os.environ["BLOG_ID"]
    post_as_draft = os.environ.get("POST_AS_DRAFT", "true").lower() != "false"

    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    report_date_str = f"{now.year}년 {now.month}월 {now.day}일 {WEEKDAYS_KR[now.weekday()]}"

    issue_no = get_next_issue_number()
    research_note = get_research_note()

    title, content_html, usage = generate_report(api_key, issue_no, report_date_str, research_note)

    access_token = refresh_google_access_token(google_client_id, google_client_secret, google_refresh_token)
    result = post_to_blogger(blog_id, access_token, title, content_html, post_as_draft)

    print(
        json.dumps(
            {
                "issue_no": issue_no,
                "title": title,
                "is_draft": post_as_draft,
                "used_research_note": research_note is not None,
                "postUrl": result.get("url"),
                "postId": result.get("id"),
                "usage": usage,  # stage0/1/2/3 별 토큰 사용량
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
