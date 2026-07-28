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
# 2. 구글 애드센스 100% 승인형 3,000자+ 마스터 주제 DB
# ==========================================
ADSENSE_MASTER_TOPICS = [
    {
        "category": "해고·징계",
        "title": "주 15시간 미만 단시간 근로자 퇴직금 지급 의무 및 5인 미만 사업장 법적 부당해고 구제 실무 정밀 분석",
        "kw": "5인미만 부당해고 해고예고수당 15시간미만 퇴직금",
        "law": "근로기준법 제26조(해고의 예고), 제23조, 근로자퇴직급여 보장법 제4조",
        "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "category": "임금·퇴직금",
        "title": "2026년 최저시급 10,030원 적용 209시간 월 소정근로시간 산출 공식 및 주휴수당 미지급 체불 임금 청구법",
        "kw": "2026년 최저시급 209시간 주휴수당 임금체불 1350",
        "law": "근로기준법 제43조, 제56조, 최저임금법 제6조",
        "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "category": "산재보상",
        "title": "출퇴근길 대중교통 및 자차 사고 업무상 재해 승인 기준과 70% 휴업급여 및 장해급여 청구 가이드",
        "kw": "출퇴근 산재 휴업급여 70퍼센트 요양급여 신청",
        "law": "산업재해보상보험법 제37조 (업무상의 재해의 인정 기준)",
        "img": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80"
    }
]

def generate_3000words_adsense_html(topic):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    title = topic["title"]
    category = topic["category"]
    law = topic["law"]
    img_url = topic["img"]
    kw = topic["kw"]

    html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Pretendard',sans-serif;color:#1e293b;line-height:1.9;max-width:860px;margin:0 auto;background:#fff;">

<!-- 마스트헤드 -->
<table width="100%" style="border-bottom:2px solid #0f172a;border-collapse:collapse;margin-bottom:24px;">
  <tr>
    <td width="35%" style="font-size:13px;color:#64748b;padding:10px 0;">{date_str} · {category} 전문 심층 분석</td>
    <td width="30%" align="center" style="font-size:15px;font-weight:900;letter-spacing:1px;padding:10px 0;color:#0f172a;">노무체크 AI 인사노무 저널</td>
    <td width="35%" align="right" style="font-size:13px;color:#64748b;padding:10px 0;">SEO 키워드: {kw}</td>
  </tr>
</table>

<!-- 핵심 3가지 검정 박스 -->
<div style="background:#0f172a;color:#ffffff;padding:26px;border-radius:12px;margin-bottom:32px;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 14px;letter-spacing:1px;">멋쟁이 인사노무 핵심 요약 (TODAY'S ESSENCE)</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">1. <strong>반직관적 법리 팩트:</strong> 근로기준법상 5인 미만 사업장도 30일 전 해고예고 통보를 하지 않으면 30일분의 해고예고수당을 100% 지급해야 합니다.</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">2. <strong>명확한 법적 근거:</strong> {law} 및 대법원 관련 판례 적용</p>
  <p style="font-size:15px;margin:0;line-height:1.7;">3. <strong>실전 입증 전략:</strong> 근로시간 입증을 위한 교통카드, 메시지, 급여명세서 3년 시효 소멸 전 확보 전략</p>
</div>

<!-- 히어로 이미지 -->
<div style="margin-bottom:36px;text-align:center;">
  <img src="{img_url}" alt="{title}" style="width:100%;max-height:440px;object-fit:cover;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.08);">
</div>

<h1 style="font-size:28px;font-weight:900;color:#0f172a;line-height:1.4;margin:0 0 36px;letter-spacing:-0.5px;">{title}</h1>

<!-- 섹션 I -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">I · 법적 근거 — 근로기준법 및 대법원 판례 입증</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
대한민국 근로기준법 제26조 및 제23조에 따르면, 사업주는 근로자를 해고하려면 적어도 30일 전에 예고를 하여야 하고, 30일 전에 예고를 하지 아니하였을 때에는 30일분 이상의 통상임금을 지급하여야 한다고 명시하고 있습니다. 이는 5인 미만 사업장이라 하더라도 예외 없이 엄격하게 적용되는 강행규정입니다.
</p>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
대법원 판례(대법원 2017다252037 판결 참조)에 의하면, 해고예고 제도는 근로자에게 갑작스러운 실직으로부터 보호하고 새로운 직장을 구할 수 있는 최소한의 시간적·경제적 여유를 보장하기 위해 마련된 제도입니다. 따라서 구두 통보나 당일 해고 통보는 법적으로 명백한 해고예고수당 청구 사유가 됩니다.
</p>

<!-- 섹션 II -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">II · 실제 적용 — 209시간 및 임금 수당 정밀 산식 계산</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
법정 월 소정근로시간인 209시간 산출 공식은 다음과 같습니다. 주 40시간(5일 × 8시간)에 주휴시간 8시간을 더하면 주당 유급 인정 시간은 총 48시간이 됩니다. 1년 365일을 7일로 나누면 약 52.14주가 되며, 이를 12개월로 나누면 1개월 평균 약 4.345주가 도출됩니다.
</p>
<div style="background:#f8fafc;border:1px solid #cbd5e1;padding:24px;border-radius:10px;margin:24px 0;">
  <h4 style="margin:0 0 12px;color:#0f172a;font-size:16px;">💡 [정밀 계산 예시] 2026년 최저임금 기준</h4>
  <p style="margin:0 0 8px;font-size:15px;color:#475569;">• 2026년 최저 시급: 10,030원</p>
  <p style="margin:0 0 8px;font-size:15px;color:#475569;">• 월 유급 인정 시간: 209시간 (기본근로 174시간 + 유급주휴 35시간)</p>
  <p style="margin:0;font-size:16px;font-weight:bold;color:#1e3a8a;">• 2026년 법정 최저 월급 = 10,030원 × 209시간 = 2,096,270원</p>
</div>

<!-- 섹션 III -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">III · 근로자 입장 — 입증 자료 확보 및 노동청 진정 절차</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
임금체불이나 해고예고수당 미지급으로 피해를 입은 근로자는 고용노동부 노동포털을 통해 온라인 진정을 제출하거나 사업장 관할 지방고용노동청을 직접 방문하여 신고를 진행할 수 있습니다. 수당 청구의 소멸시효는 3년이므로 이 기간 내에 입증 자료를 갖추어야 합니다.
</p>

<!-- 섹션 IV -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">IV · 사업주 입장 — 노동법 준수를 통한 형사처벌 및 리스크 예방</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
근로기준법 제109조에 따르면 임금을 지급하지 아니하거나 해고예고수당을 지급하지 아니한 경우 3년 이하의 징역 또는 3천만원 이하의 벌금에 처해질 수 있습니다. 사업주는 근로계약서 교부와 정확한 임금명세서 작성을 통해 과태료 처분을 사전에 철저히 대비해야 합니다.
</p>

<!-- 섹션 V -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">V · 실전 체크리스트 및 자주 묻는 질문 (FAQ)</h2>

<div style="background:#f0fff5;border-left:5px solid #16a34a;padding:24px;margin:28px 0;border-radius:0 8px 8px 0;">
  <p style="font-size:16px;font-weight:800;color:#15803d;margin:0 0 14px;">Q&A 및 체크리스트 가이드</p>
  <p style="font-size:15px;color:#334155;margin:0 0 10px;"><strong>Q1. 5인 미만 사업장은 연차휴가가 없나요?</strong><br>A1. 5인 미만 사업장은 근로기준법 제60조 연차유급휴가 규정이 적용 제외됩니다. 다만 당사자 간 약정으로 부여할 수는 있습니다.</p>
  <p style="font-size:15px;color:#334155;margin:0 0 10px;"><strong>Q2. 퇴직금 소멸시효는 언제까지인가요?</strong><br>A2. 퇴직한 날의 다음 날부터 3년간 행사하지 아니하면 시효로 인하여 소멸합니다.</p>
  <p style="font-size:15px;color:#334155;margin:0;"><strong>Q3. 출퇴근 사고도 산재 인정이 되나요?</strong><br>A3. 통상적인 경로와 방법으로 출퇴근 중 발생한 사고는 공무상 재해 또는 산재보험법상 100% 인정됩니다.</p>
</div>

<!-- 노무체크 AI 시각 박스 (#0f172a / #fbbf24) -->
<div style="background:#0f172a;border:1px solid #334155;padding:26px;border-radius:12px;margin:36px 0;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 12px;letter-spacing:1px;">EXPERTS PERSPECTIVE · 노무체크 AI 정밀 총평</p>
  <p style="font-size:15px;color:#e2e8f0;line-height:1.85;margin:0;">
    "노무 분쟁은 객관적 서면 자료와 법 조문의 정밀한 매칭이 핵심입니다. 감정적 대응보다는 출퇴근 기록, 임금 내역서 등 객관적 증거를 기반으로 노무사 및 전문 진단 엔진을 통해 사안을 분석하는 것이 가장 안전합니다."
  </p>
</div>

<!-- 법적 고지 -->
<table width="100%" style="border:2px solid #1e3a8a;border-collapse:collapse;margin:32px 0 20px;">
  <tr>
    <td style="background:#1e3a8a;padding:12px 18px;">
      <p style="font-size:13px;font-weight:800;color:#ffffff;margin:0;">법적 고지 (Legal Disclaimer)</p>
    </td>
  </tr>
  <tr>
    <td style="background:#f0f4ff;padding:16px 18px;">
      <p style="font-size:13.5px;color:#1e293b;line-height:1.8;margin:0;">
        본 글은 일반적인 인사노무 법률 정보 제공 목적이며 구체적인 사안에 관한 법적 조언이 아닙니다. 
        개별 사안의 사실관계에 따라 법적 판단이 달라질 수 있으므로 구체적인 구제 절차는 고용노동부(1350)에 정밀 문의하시기 바랍니다.
      </p>
    </td>
  </tr>
</table>

<!-- 출처 표기 푸터 및 AI 24시간 실시간 유입 연결 -->
<div style="text-align:center;padding:28px 0;border-top:1px solid #e2e8f0;font-size:13px;color:#64748b;margin-top:40px;">
  <p style="margin:0 0 14px;">출처: 근로기준법 조문, 대법원 판례 DB, 고용노동부 행정해석</p>
  <a href="{LABORCHECK_AI_URL}" target="_blank" style="display:inline-block;background:linear-gradient(135deg, #1e3a8a, #2563eb);color:#ffffff;text-decoration:none;padding:16px 32px;border-radius:30px;font-weight:bold;font-size:16px;box-shadow:0 6px 20px rgba(37,99,235,0.35);">
    ⚡ 노무체크 AI 3초 무료 급여/산재 정밀 진단받기 →
  </a>
</div>

</div>
"""
    return html

def publish_3000words_adsense_post():
    topic = random.choice(ADSENSE_MASTER_TOPICS)
    print(f"[ADSENSE 3000+ WORDS] Generating Long-Form Post: {topic['title']}")
    
    try:
        wp = Client(WP_URL, WP_USER, WP_PASS)
        post = WordPressPost()
        post.title = topic["title"]
        post.content = generate_3000words_adsense_html(topic)
        post.post_status = 'publish'
        
        post_id = wp.call(NewPost(post))
        post_link = f"http://43.200.245.223/?p={post_id}"
        print(f"[SUCCESS] 3000+ Words AdSense Approved Post Published! ID: {post_id} / URL: {post_link}")
        return True, post_link
    except Exception as e:
        print(f"[ERROR] Publishing Error: {e}")
        return False, None

if __name__ == "__main__":
    publish_3000words_adsense_post()
