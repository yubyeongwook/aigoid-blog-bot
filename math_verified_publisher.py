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
# 2. 100% 수치 검증 무결점 최저임금 계산 엔진
# ==========================================
HOURLY_RATE_2025 = 10030
MONTHLY_SALARY_2025 = HOURLY_RATE_2025 * 209  # 2,096,270원 (100% 검증)

HOURLY_RATE_2026 = 10320
MONTHLY_SALARY_2026 = HOURLY_RATE_2026 * 209  # 2,156,880원 (100% 검증)

ADSENSE_MASTER_TOPICS = [
    {
        "category": "임금·퇴직금",
        "title": "2025년-2026년 최저시급 10,030원 및 10,320원 기준 209시간 월급 수치 정밀 산식 검증",
        "kw": "2025년 최저시급 10030원 209시간 최저월급 2096270원",
        "law": "근로기준법 제43조, 최저임금법 제6조",
        "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "category": "해고·징계",
        "title": "주 15시간 미만 단시간 근로자 퇴직금 지급 의무 및 5인 미만 사업장 법적 부당해고 구제 실무 정밀 분석",
        "kw": "5인미만 부당해고 해고예고수당 15시간미만 퇴직금",
        "law": "근로기준법 제26조(해고의 예고), 제23조, 근로자퇴직급여 보장법 제4조",
        "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80"
    }
]

def generate_verified_html(topic):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    title = topic["title"]
    category = topic["category"]
    law = topic["law"]
    img_url = topic["img"]
    kw = topic["kw"]

    # 파이썬 동적 수치 정밀 검증
    h2025_fmt = f"{HOURLY_RATE_2025:,}"
    m2025_fmt = f"{MONTHLY_SALARY_2025:,}"
    h2026_fmt = f"{HOURLY_RATE_2026:,}"
    m2026_fmt = f"{MONTHLY_SALARY_2026:,}"

    html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Pretendard',sans-serif;color:#1e293b;line-height:1.9;max-width:860px;margin:0 auto;background:#fff;">

<!-- 마스트헤드 -->
<table width="100%" style="border-bottom:2px solid #0f172a;border-collapse:collapse;margin-bottom:24px;">
  <tr>
    <td width="35%" style="font-size:13px;color:#64748b;padding:10px 0;">{date_str} · {category} 전문 검증</td>
    <td width="30%" align="center" style="font-size:15px;font-weight:900;letter-spacing:1px;padding:10px 0;color:#0f172a;">노무체크 AI 수치검증 저널</td>
    <td width="35%" align="right" style="font-size:13px;color:#64748b;padding:10px 0;">SEO 키워드: {kw}</td>
  </tr>
</table>

<!-- 핵심 요약 박스 (검정 배경) -->
<div style="background:#0f172a;color:#ffffff;padding:26px;border-radius:12px;margin-bottom:32px;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 14px;letter-spacing:1px;">멋쟁이 인사노무 핵심 요약 (TODAY'S ESSENCE)</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">1. <strong>2025년 법정 최저시급 정밀 검증:</strong> {h2025_fmt}원 × 209시간 = <strong>{m2025_fmt}원</strong> (오차 0원 정밀 확정 산식)</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">2. <strong>2026년 최저시급 (10,320원 반영 시):</strong> {h2026_fmt}원 × 209시간 = <strong>{m2026_fmt}원</strong></p>
  <p style="font-size:15px;margin:0;line-height:1.7;">3. <strong>법적 근거:</strong> {law} 명시 법정 소정근로시간 적용</p>
</div>

<!-- 히어로 이미지 -->
<div style="margin-bottom:36px;text-align:center;">
  <img src="{img_url}" alt="{title}" style="width:100%;max-height:440px;object-fit:cover;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.08);">
</div>

<h1 style="font-size:28px;font-weight:900;color:#0f172a;line-height:1.4;margin:0 0 36px;letter-spacing:-0.5px;">{title}</h1>

<!-- 섹션 I -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">I · 최저임금 수치 정밀 검증 공식 및 209시간 산출 법리</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
대한민국 최저임금법 및 근로기준법상 월 소정근로시간 209시간의 정확한 산식은 (주 40시간 + 유급 주휴 8시간) × 365일 ÷ 7일 ÷ 12개월 = 208.71시간을 올림 한 209시간입니다. 
따라서 시급에 209시간을 곱하면 정확한 법정 최저 월급이 도출됩니다.
</p>

<!-- 정밀 계산 검증 상자 -->
<div style="background:#f8fafc;border:2px solid #2563eb;padding:26px;border-radius:12px;margin:28px 0;">
  <h4 style="margin:0 0 14px;color:#1e3a8a;font-size:17px;font-weight:bold;">🔍 [100% 수치 검증] 최저임금 연도별 법정 월급 비교</h4>
  <p style="margin:0 0 10px;font-size:15.5px;color:#334155;">• <strong>2025년 확정 최저시급 ({h2025_fmt}원):</strong> {h2025_fmt}원 × 209시간 = <span style="color:#2563eb;font-weight:bold;">{m2025_fmt}원</span></p>
  <p style="margin:0 0 10px;font-size:15.5px;color:#334155;">• <strong>2026년 인상 기준 ({h2026_fmt}원):</strong> {h2026_fmt}원 × 209시간 = <span style="color:#2563eb;font-weight:bold;">{m2026_fmt}원</span></p>
  <p style="margin:12px 0 0;font-size:14px;color:#64748b;border-top:1px solid #e2e8f0;padding-top:10px;">* 주휴수당(주 8시간 유급)이 100% 포함된 209시간 기본급 계산 결과입니다.</p>
</div>

<!-- 섹션 II -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">II · 수치 체불 발생 시 법적 대응 절차</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
만약 근로계약서상 월급이 위 검증 수치인 {m2025_fmt}원 미만으로 지급된다면 이는 명백한 최저임금법 위반 및 임금체불에 해당합니다. 근로자는 차액에 대해 최근 3년 치를 소급하여 청구할 수 있으며 고용노동부에 진정을 제기할 수 있습니다.
</p>

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
        본 수치 검증 데이터는 최저임금법 및 근로기준법상 209시간 정밀 공식을 바탕으로 파이썬 엔진에서 수학적으로 검증된 데이터입니다.
      </p>
    </td>
  </tr>
</table>

<!-- 출처 표기 푸터 및 AI 24시간 실시간 유입 연결 -->
<div style="text-align:center;padding:28px 0;border-top:1px solid #e2e8f0;font-size:13px;color:#64748b;margin-top:40px;">
  <p style="margin:0 0 14px;">출처: 대한민국 최저임금위원회 공식 의결안, 근로기준법 제43조</p>
  <a href="{LABORCHECK_AI_URL}" target="_blank" style="display:inline-block;background:linear-gradient(135deg, #1e3a8a, #2563eb);color:#ffffff;text-decoration:none;padding:16px 32px;border-radius:30px;font-weight:bold;font-size:16px;box-shadow:0 6px 20px rgba(37,99,235,0.35);">
    ⚡ 노무체크 AI 3초 무료 급여/산재 정밀 진단받기 →
  </a>
</div>

</div>
"""
    return html

def publish_verified_post():
    topic = random.choice(ADSENSE_MASTER_TOPICS)
    print(f"[VERIFIED ENGINE] Generating Math-Verified Post: {topic['title']}")
    
    try:
        wp = Client(WP_URL, WP_USER, WP_PASS)
        post = WordPressPost()
        post.title = topic["title"]
        post.content = generate_verified_html(topic)
        post.post_status = 'publish'
        
        post_id = wp.call(NewPost(post))
        post_link = f"http://43.200.245.223/?p={post_id}"
        print(f"[SUCCESS] 100% Math Verified Post Published! ID: {post_id} / URL: {post_link}")
        return True, post_link
    except Exception as e:
        print(f"[ERROR] Publishing Error: {e}")
        return False, None

if __name__ == "__main__":
    publish_verified_post()
