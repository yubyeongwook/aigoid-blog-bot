import os
import random
import time
import requests
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# ==========================================
# 1. AWS Lightsail WordPress XML-RPC 설정
# ==========================================
WP_URL = "http://43.200.245.223/xmlrpc.php"
WP_USER = "user"
WP_PASS = "LaborCheck123!"

LABORCHECK_AI_URL = "https://laborcheck-ai.vercel.app"

# ==========================================
# 2. 제미나이 노무 블로그 트래픽 핵심 주제 DB
# ==========================================
LABOR_MASTER_TOPICS = [
    {
        "category": "임금·퇴직금",
        "title": "주 15시간 미만이면 퇴직금이 없다는 건 절반만 맞는 말이다",
        "kw": "퇴직금 계선방법 근로시간 주휴수당",
        "law": "근로기준법 제34조, 근로자퇴직급여 보장법 제4조",
        "counter": "4주간을 평균하여 1주 15시간 이상 근무한 기간이 전체 재직기간 중 1년 이상이면 퇴직금 청구권이 발생합니다.",
        "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "category": "연차·휴가",
        "title": "1년 미만 근무자는 연차가 없다는 건 완전한 오해다",
        "kw": "1년미만 연차휴가 근로기준법60조",
        "law": "근로기준법 제60조 제2항",
        "counter": "1년 미만 근무자도 1개월 개근 시 1일의 유급휴가가 발생하여 입사 첫해 최대 11일의 연차가 부여됩니다.",
        "img": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "category": "해고·징계",
        "title": "5인 미만 사업장에서 부당해고 당하면 정말 아무것도 못 하는가",
        "kw": "5인미만 부당해고 해고예고수당 노동위원회",
        "law": "근로기준법 제26조 (해고의 예고), 제23조",
        "counter": "5인 미만 사업장도 30일 전 해고예고를 하지 않으면 30일분의 해고예고수당을 반드시 지급해야 합니다.",
        "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "category": "근로시간·초과근무",
        "title": "포괄임금제 계약서를 썼으니 야간수당을 못 받는다는 건 틀린 말이다",
        "kw": "포괄임금제 무효 연장수당 야간수당",
        "law": "근로기준법 제56조, 대법원 2010다26390 판결",
        "counter": "근로시간 산정이 가능함에도 맺은 포괄임금 약정은 법적으로 무효이며 실제 초과근로시간에 따른 수당 차액을 청구할 수 있습니다.",
        "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80"
    }
]

def generate_system_prompt_html(topic):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    title = topic["title"]
    category = topic["category"]
    law = topic["law"]
    counter = topic["counter"]
    img_url = topic["img"]
    kw = topic["kw"]

    html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Pretendard',sans-serif;color:#1a1a1a;line-height:1.95;max-width:780px;margin:0 auto;background:#fff;">

<!-- 1. 마스트헤드 (table 태그) -->
<table width="100%" style="border-bottom:2px solid #000;border-collapse:collapse;margin-bottom:24px;">
  <tr>
    <td width="30%" style="font-size:12px;color:#666;padding:8px 0;">{date_str} · {category}</td>
    <td width="40%" align="center" style="font-size:14px;font-weight:900;letter-spacing:1px;padding:8px 0;color:#000;">노무체크 AI 인사노무 저널</td>
    <td width="30%" align="right" style="font-size:12px;color:#666;padding:8px 0;">키워드: {kw}</td>
  </tr>
</table>

<!-- 2. 핵심 요약 박스 (검정 배경) -->
<div style="background:#0a0a0a;color:#fff;padding:24px;border-radius:8px;margin-bottom:30px;">
  <p style="font-size:13px;font-weight:700;color:#f0c040;margin:0 0 12px;letter-spacing:1px;">TODAY'S ESSENCE · 오늘 핵심 3가지</p>
  <p style="font-size:14px;margin:0 0 8px;line-height:1.7;">1. <strong>반직관적 팩트:</strong> {counter}</p>
  <p style="font-size:14px;margin:0 0 8px;line-height:1.7;">2. <strong>법적 근거:</strong> {law} 명시 규정 적용</p>
  <p style="font-size:14px;margin:0;line-height:1.7;">3. <strong>실전 대응:</strong> 3년 이내의 입증 자료 확보 시 시효 소멸 전 청구 가능</p>
</div>

<!-- 3. 히어로 이미지 -->
<div style="margin-bottom:32px;text-align:center;">
  <img src="{img_url}" alt="{title}" style="width:100%;max-height:420px;object-fit:cover;border-radius:8px;">
</div>

<!-- 4. H1 제목 (역설/숫자형) -->
<h1 style="font-size:26px;font-weight:900;color:#000;line-height:1.4;margin:0 0 32px;letter-spacing:-0.5px;">{title}</h1>

<!-- 5. 섹션 I ~ V -->
<h2 style="font-size:18px;font-weight:800;color:#1a3a6b;border-bottom:2px solid #1a3a6b;padding-bottom:8px;margin:36px 0 16px;">I · 법적 근거 — 근로기준법이 말하는 조문 팩트</h2>
<p style="font-size:14.5px;color:#2c2c2c;margin-0 0 16px;">
많은 근로자와 사업주가 현장에서 잘못 알고 있는 노무 상식 중 하나가 바로 해당 조항입니다. 
대한민국 {law}에 따르면, 명시적인 요건을 충족하는 경우 법률상 권리가 발생할 소지가 있습니다. 
단순히 소문이나 구두상 관행만을 믿고 대응할 경우 법적 불이익을 입을 수 있습니다.
</p>

<h2 style="font-size:18px;font-weight:800;color:#1a3a6b;border-bottom:2px solid #1a3a6b;padding-bottom:8px;margin:36px 0 16px;">II · 실제 적용 — 사례로 보는 현실 과제</h2>
<p style="font-size:14.5px;color:#2c2c2c;margin-0 0 16px;">
실제 고용노동부 근로감독 실무 사례에 따르면, 계약서 문구와 실제 근무 형태가 일치하지 않아 분쟁이 발생하는 사례가 다수 적발되고 있습니다. 
특히 주휴시간이나 수당 계산 시 유급 인정 범위에 관한 판단 기준에 따라 금액 차이가 크게 발생할 수 있습니다.
</p>

<h2 style="font-size:18px;font-weight:800;color:#1a3a6b;border-bottom:2px solid #1a3a6b;padding-bottom:8px;margin:36px 0 16px;">III · 근로자 입장 — 이렇게 권리를 보호하라</h2>
<p style="font-size:14.5px;color:#2c2c2c;margin-0 0 16px;">
근로자 입장에서는 입사 시 작성한 근로계약서, 매월 수령하는 임금명세서, 그리고 실제 출퇴근 기록(메시지 기록, 교통카드 내역 등)을 평소에 구체적으로 보관해 두는 것이 권리 구제 시 유용한 증거가 됩니다.
</p>

<h2 style="font-size:18px;font-weight:800;color:#1a3a6b;border-bottom:2px solid #1a3a6b;padding-bottom:8px;margin:36px 0 16px;">IV · 사업주 입장 — 이것만 지키면 임금체불 예방된다</h2>
<p style="font-size:14.5px;color:#2c2c2c;margin-0 0 16px;">
사업주 역시 정확한 법정 소정근로시간과 수당 산식에 맞춰 근로계약서를 재정비하고 임금명세서를 적법하게 교부해야 3년 이내 예기치 못한 수당 청구나 노동청 진정 리스크를 사전에 예방할 수 있습니다.
</p>

<h2 style="font-size:18px;font-weight:800;color:#1a3a6b;border-bottom:2px solid #1a3a6b;padding-bottom:8px;margin:36px 0 16px;">V · 지금 당장 할 것 — 실전 체크리스트</h2>

<!-- 6. 실전 체크리스트 박스 -->
<div style="background:#f0fff5;border-left:4px solid #1a7a4a;padding:20px;margin:24px 0;border-radius:0 6px 6px 0;">
  <p style="font-size:14px;font-weight:700;color:#1a7a4a;margin:0 0 12px;">지금 당장 확인할 필수 실전 수칙</p>
  <p style="font-size:13.5px;color:#2c2c2c;margin:0 0 8px;">□ 근로계약서 작성 및 교부 상태 재확인</p>
  <p style="font-size:13.5px;color:#2c2c2c;margin:0 0 8px;">□ 임금명세서 항목별 수당 계산 산식 확인</p>
  <p style="font-size:13.5px;color:#2c2c2c;margin:0 0 8px;">□ 실제 출퇴근 근로시간 기록 객관적 메모 보관</p>
  <p style="font-size:13.5px;color:#2c2c2c;margin:0;">□ 고용노동부 상담센터 (국번없이 1350) 활용</p>
</div>

<!-- 7. 멋쟁이 노무 시각 박스 (검정 #0a0a0a / 골드 #f0c040) -->
<div style="background:#0a0a0a;border:1px solid #333;padding:24px;border-radius:8px;margin:32px 0;">
  <p style="font-size:13px;font-weight:700;color:#f0c040;margin:0 0 10px;letter-spacing:1px;">EXPERTS PERSPECTIVE · 노무체크 AI 인사이트</p>
  <p style="font-size:14px;color:#e2e8f0;line-height:1.8;margin:0;">
    "노무 분쟁의 90%는 법 조문을 몰라서가 아니라, 객관적 입증 자료 부족과 잘못된 인터넷 상식 신봉에서 출발합니다. 정확한 법령 조문과 전문가의 판단 기준을 바탕으로 사안을 냉철하게 파악하는 것이 가장 중요합니다."
  </p>
</div>

<!-- 8. 법적 고지 (필수) -->
<table width="100%" style="border:2px solid #1a3a6b;border-collapse:collapse;margin:28px 0 16px;">
  <tr>
    <td style="background:#1a3a6b;padding:10px 16px;">
      <p style="font-size:12px;font-weight:700;color:#fff;margin:0;">법적 고지 (Legal Disclaimer)</p>
    </td>
  </tr>
  <tr>
    <td style="background:#f0f4ff;padding:14px 16px;">
      <p style="font-size:12.5px;color:#1a2a4a;line-height:1.8;margin:0;">
        본 글은 일반적인 노무 정보 제공 목적이며 구체적인 개별 법적 조언이 아닙니다. 
        개별 사안에 따라 적용 내용이 다를 수 있으므로 구체적인 판단 및 절차는 고용노동부(1350)에 문의하시기 바랍니다.
      </p>
    </td>
  </tr>
</table>

<!-- 9. 출처 표기 푸터 및 AI 24시간 연결 바 -->
<div style="text-align:center;padding:20px 0;border-top:1px solid #eee;font-size:12px;color:#888;">
  <p style="margin:0 0 10px;">출처: 근로기준법 조문, 고용노동부 행정해석, 대법원 판례 DB</p>
  <a href="{LABORCHECK_AI_URL}" target="_blank" style="display:inline-block;background:#2563eb;color:#fff;text-decoration:none;padding:12px 24px;border-radius:25px;font-weight:bold;font-size:14px;">
    ⚡ 노무체크 AI 3초 무료 급여/산재 정밀 진단 →
  </a>
</div>

</div>
"""
    return html

def publish_master_post():
    topic = random.choice(LABOR_MASTER_TOPICS)
    print(f"[SYSTEM PROMPT SYSTEM] Generating Post: {topic['title']}")
    
    try:
        wp = Client(WP_URL, WP_USER, WP_PASS)
        post = WordPressPost()
        post.title = topic["title"]
        post.content = generate_system_prompt_html(topic)
        post.post_status = 'publish'
        
        post_id = wp.call(NewPost(post))
        post_link = f"http://43.200.245.223/?p={post_id}"
        print(f"[SUCCESS] Master System Prompt Post Published! ID: {post_id} / URL: {post_link}")
        return True, post_link
    except Exception as e:
        print(f"[ERROR] Publishing Error: {e}")
        return False, None

if __name__ == "__main__":
    publish_master_post()
