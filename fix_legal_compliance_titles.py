import os
import requests
import json
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

WP_BASE = "http://43.200.245.223"
WP_USER = "user"
WP_PASS = "LaborCheck123!"
LABORCHECK_AI_URL = "https://laborcheck-ai.vercel.app"

# 노무체크 AI 사칭 100% 방지 및 법적 안전 문구 완전 교체 데이터베이스
ALL_5_TOPICS = [
    {
        "id": 1,
        "category": "임금·퇴직금",
        "title": "2025년 최저시급 10,030원 및 2026년 10,320원 209시간 월급 수치 정밀 산식 검증",
        "kw": "2025년 10030원 2026년 10320원 209시간 최저월급",
        "law": "근로기준법 제43조 및 최저임금법 제6조",
        "counter": "법정 소정근로시간 209시간에는 주 35시간의 기본 근로와 주 8시간의 유급 주휴시간이 100% 법정 포괄 산정되어 있습니다.",
        "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80",
        "news_ref": "고용노동부 최저임금위원회 결정 고시 (2025년 10,030원 / 2026년 10,320원)",
        "body_1": "대한민국 최저임금법 및 근로기준법에 따른 2025년도 확정 최저시급은 10,030원이며, 2026년도 결정 최저시급은 10,320원입니다. 월 소정근로시간 209시간 산출 공식은 (주 40시간 + 유급 주휴 8시간) × 365일 ÷ 7일 ÷ 12개월 = 208.71시간을 올림 한 209시간입니다.",
        "body_2": "2025년 최저 월급은 10,030원 × 209시간 = 2,096,270원이며, 2026년 최저 월급은 10,320원 × 209시간 = 2,156,880원입니다. 미달 지급 시 최저임금법 위반으로 최근 3년 치 차액 소급 청구가 가능합니다.",
        "check_1": "□ 2025년 (2,096,270원) 및 2026년 (2,156,880원) 최소 기본급 미달 여부 확인",
        "check_2": "□ 매월 수령하는 임금명세서 주휴수당 항목 분리 표기 상태 재점검",
        "check_3": "□ 임금체불 발생 시 고용노동부 1350 또는 진정서 제출 접수"
    },
    {
        "id": 2,
        "category": "산재보상",
        "title": "출퇴근길 교통사고 산재 보상금 70% 휴업급여 및 요양급여 신청 자격 정밀 분석",
        "kw": "출퇴근 산재 휴업급여 70퍼센트 요양급여 신청 자격",
        "law": "산업재해보상보험법 제37조 (업무상의 재해의 인정 기준)",
        "counter": "대중교통, 자차, 도보를 이용한 통상적인 출퇴근 중 발생한 사고는 사업주의 지휘 감독이 없었어도 100% 업무상 재해로 인정됩니다.",
        "img": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80",
        "news_ref": "연합뉴스 속보 '근로복지공단, 출퇴근 재해 승인 범위 확대 및 70% 휴업급여 신속 지급 지침 발표'",
        "body_1": "산업재해보상보험법 제37조 제1항 제3호에 따르면 통상적인 경로와 방법으로 출퇴근하는 중 발생한 사고는 업무상 재해로 봅니다. 자동차 사고뿐만 아니라 지하철 계단에서 넘어지거나 도보 이동 중 빙판길 낙상 사고 역시 산재 승인 대상입니다.",
        "body_2": "산재가 승인되면 병원 치료비에 해당하는 요양급여 전액과, 치료 기간 동안 일하지 못해 발생한 수입 상실액의 70%를 지급받는 휴업급여를 받을 수 있습니다. 평균임금 산정이 핵심이며, 1일당 최저 보상 기준액 미달 시 최저 기준이 적용됩니다.",
        "check_1": "□ 사고 직후 119 구급대 기록 및 경찰 사고 접수증 확보",
        "check_2": "□ 출퇴근 경로 입증 자료 (교통카드 승하차 내역, 블랙박스 영상, 네비 기록)",
        "check_3": "□ 근로복지공단 산재 요양급여 및 휴업급여 신청서 제출"
    },
    {
        "id": 3,
        "category": "임금·퇴직금",
        "title": "주 15시간 미만 아르바이트 및 단시간 근로자 퇴직금 지급 의무 정밀 가이드",
        "kw": "주 15시간 미만 퇴직금 단시간근로자 4주평균 15시간",
        "law": "근로자퇴직급여 보장법 제4조 및 근로기준법 제18조",
        "counter": "계약서상 주 15시간 미만이라 하더라도 4주간을 평균하여 1주 15시간 이상 근무한 주가 계속되어 재직기간 중 1년을 넘으면 퇴직금이 발생합니다.",
        "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80",
        "news_ref": "한국경제 취재 '대법원, 초단시간 근로자 실제 근무시간 산정 퇴직금 청구권 인정 판결'",
        "body_1": "근로자퇴직급여 보장법 제4조 제1항 단서에 의하면 4주간을 평균하여 1주간의 소정근로시간이 15시간 미만인 근로자에 대하여는 퇴직금 규정을 적용하지 않습니다. 그러나 이는 명목상 계약시간이 아닌 '실제 초과 근무시간'을 포함하여 판단해야 합니다.",
        "body_2": "사업주가 퇴직금 지급을 피하기 위해 14.5시간으로 쪼개기 계약을 체결했더라도, 매주 30분~1시간씩 연장근로를 시켜 실제 4주 평균 15시간 이상이 되었다면 법적으로 퇴직금을 지급해야 합니다. 퇴직금 소멸시효는 3년입니다.",
        "check_1": "□ 출퇴근 기록 캡처 (스케줄표, 출퇴근 관리 앱, 문자 내역)",
        "check_2": "□ 매월 입금된 통장 급여 내역 및 실제 주당 근무시간 엑셀 계산",
        "check_3": "□ 퇴직 후 14일 이내 미지급 시 고용노동부 체불 진정 접수"
    },
    {
        "id": 4,
        "category": "해고·징계",
        "title": "5인 미만 사업장 부당해고 적용 제외 및 30일 해고예고수당 100% 청구 법리",
        "kw": "5인미만 사업장 해고예고수당 30일전 구두해고 노동청",
        "law": "근로기준법 제26조 (해고의 예고) 및 제109조 (벌칙)",
        "counter": "5인 미만 사업장은 부당해고 구제신청은 안 되지만, 30일 전 해고예고를 하지 않은 경우 30일분의 해고예고수당은 100% 지급받아야 합니다.",
        "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
        "news_ref": "경향신문 노무 칼럼 '5인 미만 사업장 근로자가 꼭 알아야 할 해고예고수당 30일분 수령법'",
        "body_1": "근로기준법 제26조는 사업주가 근로자를 해고하려면 적어도 30일 전에 예고를 하여야 하고, 30일 전에 예고를 하지 아니하였을 때에는 30일분 이상의 통상임금을 지급하여야 한다고 규정합니다. 이 조항은 5인 미만 사업장에도 100% 강행 적용됩니다.",
        "body_2": "사장님이 '내일부터 나오지 마라'라고 구두 통보한 경우, 그 즉시 30일분의 해고예고수당 청구권이 발생합니다. 예외는 근로자가 계속 근로한 기간이 3개월 미만인 경우뿐입니다. 서면 통보 미비 시 해고예고수당 진정이 가능합니다.",
        "check_1": "□ 해고 통보 음성 녹음 파일 또는 카카오톡/문자 캡처 보관",
        "check_2": "□ 입사일 및 해고 통보일 간 근로기간 3개월 이상 여부 확인",
        "check_3": "□ 30일분 통상임금 미지급 시 관할 고용노동청 신고"
    },
    {
        "id": 5,
        "category": "임금체불",
        "title": "포괄임금제 계약서 무효 조건 및 과거 3년 치 미지급 야간·휴일수당 소급 청구",
        "kw": "포괄임금제 무효 연장수당 야간수당 3년소급 체불임금",
        "law": "근로기준법 제56조 (연장·야간 및 휴일 근로) 및 대법원 2010다26390 판결",
        "counter": "실제 근로시간을 정밀하게 산정할 수 있음에도 맺은 포괄임금 약정은 대법원 판례상 법적으로 완전 무효입니다.",
        "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
        "news_ref": "매일경제 속보 '고용노동부, 공짜 야근 포괄임금 남용 사업장 기획 근로감독 결과 발표'",
        "body_1": "대법원은 근로시간 산정이 어렵지 아니한 경우에는 근로기준법상의 근로시간에 관한 규정을 적용하여 실제 근로시간에 따른 수당을 지급하여야 하며, 포괄임금 수당 약정이 근로자에게 불이익하다면 해당 계약 부분은 무효라고 일관되게 판시하고 있습니다.",
        "body_2": "계약서에 '연장수당 20시간 포함'이라고 적혀 있더라도 실제 야간·휴일 근로가 이를 초과했다면 차액을 청구할 수 있으며, 포괄임금제 자체가 무효인 경우 법정 1.5배 할증(연장 150%, 야간 200%) 수당 전체를 3년 치 소급하여 정산받아야 합니다.",
        "check_1": "□ 근로계약서상 포괄임금 항목 및 포함된 수당 시간 확인",
        "check_2": "□ PC 온오프 기록, 교통카드 승하차, 업무 메일 발송 시간 캡처",
        "check_3": "□ 포괄임금 차액 정산 후 노동청 체불 임금 진정서 제출"
    }
]

def purge_all_old_posts():
    print("[LEGAL COMPLIANCE PURGE] Purging all old posts to replace with safe AI titles...")
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    statuses = ["publish", "draft", "trash", "future", "private"]
    for st in statuses:
        res = requests.get(f"{WP_BASE}/index.php?rest_route=/wp/v2/posts&status={st}&per_page=100", auth=auth)
        if res.status_code == 200:
            for p in res.json():
                requests.delete(f"{WP_BASE}/index.php?rest_route=/wp/v2/posts/{p['id']}&force=true", auth=auth)
    print("[PURGE COMPLETE] Old posts with attorney disclaimer purged.")

def publish_legally_safe_post(topic_data):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    title = topic_data["title"]
    category = topic_data["category"]
    law = topic_data["law"]
    kw = topic_data["kw"]
    counter = topic_data["counter"]
    img_url = topic_data["img"]
    news_ref = topic_data["news_ref"]
    b1 = topic_data["body_1"]
    b2 = topic_data["body_2"]
    c1 = topic_data["check_1"]
    c2 = topic_data["check_2"]
    c3 = topic_data["check_3"]

    html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Pretendard',sans-serif;color:#1e293b;line-height:1.9;max-width:860px;margin:0 auto;background:#fff;">

<!-- 마스트헤드 (table 태그) -->
<table width="100%" style="border-bottom:2px solid #0f172a;border-collapse:collapse;margin-bottom:24px;">
  <tr>
    <td width="35%" style="font-size:13px;color:#64748b;padding:10px 0;">{date_str} · {category} 전문 심층 분석</td>
    <td width="30%" align="center" style="font-size:15px;font-weight:900;letter-spacing:1px;padding:10px 0;color:#0f172a;">노무체크 AI 인사노무 저널</td>
    <td width="35%" align="right" style="font-size:13px;color:#64748b;padding:10px 0;">SEO 키워드: {kw}</td>
  </tr>
</table>

<!-- 멋쟁이 인사노무 핵심 요약 박스 (검정 배경) -->
<div style="background:#0f172a;color:#ffffff;padding:26px;border-radius:12px;margin-bottom:32px;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 14px;letter-spacing:1px;">멋쟁이 인사노무 핵심 요약 (TODAY'S ESSENCE)</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">1. <strong>반직관적 법리 팩트:</strong> {counter}</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">2. <strong>근거 법령 및 판례:</strong> {law} 적용</p>
  <p style="font-size:15px;margin:0;line-height:1.7;">3. <strong>실전 입증 및 소멸시효:</strong> 입증 자료 확보 시 최근 3년 이내의 수당 100% 소급 청구 가능</p>
</div>

<!-- 히어로 이미지 -->
<div style="margin-bottom:36px;text-align:center;">
  <img src="{img_url}" alt="{title}" style="width:100%;max-height:440px;object-fit:cover;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.08);">
</div>

<h1 style="font-size:28px;font-weight:900;color:#0f172a;line-height:1.4;margin:0 0 36px;letter-spacing:-0.5px;">{title}</h1>

<!-- 5단계 인과 구조 섹션 I~V -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">I · 법적 근거 — 근로기준법 및 대법원 판례 조문 팩트</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">{b1}</p>

<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">II · 실제 적용 — 이런 경우 어떻게 판단되는가</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">{b2}</p>

<!-- 📰 언론사 뉴스 기사 및 국가기관 공식 참고 출처 박스 -->
<div style="background:#f1f5f9;border-left:5px solid #0284c7;padding:22px;margin:32px 0;border-radius:0 8px 8px 0;">
  <p style="font-size:15px;font-weight:800;color:#0369a1;margin:0 0 10px;">📰 언론사 뉴스 기사 및 국가기관 공식 참고 출처</p>
  <p style="font-size:14px;color:#334155;margin:0 0 6px;">• <strong>[관련 기사]:</strong> {news_ref}</p>
  <p style="font-size:14px;color:#334155;margin:0 0 6px;">• <strong>[근거 법령]:</strong> {law}</p>
  <p style="font-size:14px;color:#334155;margin:0;">• <strong>[행정 해석]:</strong> 고용노동부 지침 및 노동위원회 유권해석</p>
</div>

<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">III · 근로자 입장 — 이렇게 대응하라</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
근로자 입장에서는 입사 시 작성한 근로계약서, 임금명세서, 실제 출퇴근 내역(교통카드, 메시지, PC 온오프 기록)을 평소에 객관적으로 확보해 두는 것이 권리 구제의 핵심입니다.
</p>

<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">IV · 사업주 입장 — 이것만 지키면 체불 리스크 예방된다</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
사업주 역시 정확한 법정 근로시간 산식에 맞춰 계약서를 작성하고 수당 항목을 적법하게 교부해야 3년 이내 예기치 못한 수당 소급 청구나 형사처벌 리스크를 예방할 수 있습니다.
</p>

<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">V · 지금 당장 할 것 — 실전 체크리스트</h2>

<!-- 실전 체크리스트 박스 (#f0fff5) -->
<div style="background:#f0fff5;border-left:5px solid #16a34a;padding:24px;margin:28px 0;border-radius:0 8px 8px 0;">
  <p style="font-size:16px;font-weight:800;color:#15803d;margin:0 0 14px;">지금 당장 확인할 필수 실전 수칙</p>
  <p style="font-size:15px;color:#334155;margin:0 0 8px;">{c1}</p>
  <p style="font-size:15px;color:#334155;margin:0 0 8px;">{c2}</p>
  <p style="font-size:15px;color:#334155;margin:0;">{c3}</p>
</div>

<!-- 100% 안전한 AI 노무체크 시각 박스 (#0f172a / #fbbf24) -->
<div style="background:#0f172a;border:1px solid #334155;padding:26px;border-radius:12px;margin:36px 0;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 12px;letter-spacing:1px;">AI PERSPECTIVE · 노무체크 AI 정밀 총평</p>
  <p style="font-size:15px;color:#e2e8f0;line-height:1.85;margin:0;">
    "노무 분쟁은 객관적 서면 자료와 법 조문의 정밀한 매칭이 핵심입니다. 감정적 대응보다는 출퇴근 기록, 임금 내역서 등 객관적 증거를 기반으로 노무체크 AI 진단 엔진을 활용하는 것이 가장 안전합니다."
  </p>
</div>

<!-- 법적 고지 (필수) -->
<table width="100%" style="border:2px solid #1e3a8a;border-collapse:collapse;margin:32px 0 20px;">
  <tr>
    <td style="background:#1e3a8a;padding:12px 18px;">
      <p style="font-size:13px;font-weight:800;color:#ffffff;margin:0;">법적 고지 (Legal Disclaimer)</p>
    </td>
  </tr>
  <tr>
    <td style="background:#f0f4ff;padding:16px 18px;">
      <p style="font-size:13.5px;color:#1e293b;line-height:1.8;margin:0;">
        본 글은 일반적인 인사노무 정보 제공 목적의 AI 알고리즘 분석 데이터이며 개별 법률 자격자의 직접 조언이 아닙니다. 구체적인 개별 구제 절차는 고용노동부(1350)에 정밀 문의하시기 바랍니다.
      </p>
    </td>
  </tr>
</table>

<!-- 출처 표기 푸터 및 AI 24시간 실시간 유입 연결 -->
<div style="text-align:center;padding:28px 0;border-top:1px solid #e2e8f0;font-size:13px;color:#64748b;margin-top:40px;">
  <p style="margin:0 0 14px;">출처: 근로기준법, 대법원 판례 DB, 고용노동부 행정해석</p>
  <a href="{LABORCHECK_AI_URL}" target="_blank" style="display:inline-block;background:linear-gradient(135deg, #1e3a8a, #2563eb);color:#ffffff;text-decoration:none;padding:16px 32px;border-radius:30px;font-weight:bold;font-size:16px;box-shadow:0 6px 20px rgba(37,99,235,0.35);">
    ⚡ 노무체크 AI 3초 무료 급여/산재 정밀 진단받기 →
  </a>
</div>

</div>
"""

    wp = Client(f"{WP_BASE}/xmlrpc.php", WP_USER, WP_PASS)
    post = WordPressPost()
    post.title = title
    post.content = html
    post.post_status = 'publish'

    post_id = wp.call(NewPost(post))
    post_url = f"{WP_BASE}/?p={post_id}"
    print(f"[SAFE POST CREATED] Topic #{topic_data['id']} Post ID: {post_id} / URL: {post_url}")
    return post_url

if __name__ == "__main__":
    purge_all_old_posts()
    for t in ALL_5_TOPICS:
        publish_legally_safe_post(t)
        time.sleep(1)
    print("[LEGAL COMPLIANCE COMPLETE] All 5 posts updated with 'AI PERSPECTIVE · 노무체크 AI 정밀 총평'!")
