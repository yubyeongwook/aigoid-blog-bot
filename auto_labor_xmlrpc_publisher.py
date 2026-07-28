import os
import random
import time
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
# 2. 트래픽 폭발 노무·산재 핵심 키워드 리스트
# ==========================================
LABOR_KEYWORDS = [
    {
        "title": "2026년 최저시급 10,030원 기준 209시간 월급 정밀 산식 및 주휴수당 계산법",
        "category": "급여계산",
        "summary": "2026년 최저임금 10,030원에 따른 월 209시간 유급 주휴시간 포함 기본급 산출 공식과 주휴수당 포함 실수령액 정밀 계산 가이드입니다."
    },
    {
        "title": "출퇴근길 교통사고 산재 보상금 100% 승인 노하우 및 요양급여 신청 자격",
        "category": "산재보상",
        "summary": "대중교통, 자차, 도보 출퇴근 중 발생한 사고의 업무상 재해 인정 기준과 70% 휴업급여 청구 절차를 완벽 정리해 드립니다."
    },
    {
        "title": "뇌출혈·심근경색 뇌심혈관계 과로 산재 승인 기준 및 12주 근로시간 입증법",
        "category": "과로산재",
        "summary": "발병 전 12주간 주 평균 60시간 이상 과로 입증 전략과 산재심의위원회 인정률을 높이는 부장판사/전문의 AI 분석 가이드입니다."
    },
    {
        "title": "무거운 물건 들다 생긴 허리디스크·관절 질환 근골격계 산재 요양 신청법",
        "category": "근골격계",
        "summary": "반복적인 신체부담 작업으로 인한 허리·어깨·목 디스크의 업무상 질병 판정 지침과 공단 승인율 70% 돌파 노하우입니다."
    },
    {
        "title": "포괄임금제 무효화 및 과거 3년 치 미지급 연장·야간·휴일수당 청구 가이드",
        "category": "임금체불",
        "summary": "근로계약서상 포괄임금 문구가 법적으로 무효가 되는 조건과 노동청 진정 제출 시 수당 정밀 계산법을 공개합니다."
    }
]

def generate_labor_post_html(keyword_info):
    title = keyword_info["title"]
    category = keyword_info["category"]
    summary = keyword_info["summary"]

    html_content = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.8; color: #1e293b; max-width: 800px; margin: 0 auto;">
  
  <div style="background: #f8fafc; border-left: 5px solid #2563eb; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
    <span style="background: #2563eb; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{category} 전문 가이드</span>
    <h2 style="margin: 12px 0 8px 0; color: #0f172a; font-size: 20px; font-weight: 700;">{title}</h2>
    <p style="margin: 0; color: #475569; font-size: 15px;">{summary}</p>
  </div>

  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; font-size: 22px;">1. 노무·산재 법률적 핵심 포인트</h2>
  <p>최근 노동법 개정 및 근로복지공단 심사 지침에 따라 임금 계산과 산재 인정 기준이 한층 정밀해졌습니다. 근로자와 사업주 모두 법정 유급 주휴시간(8시간x4.345주)과 209시간 산식을 정확히 파악해야 체불 분쟁을 예방할 수 있습니다.</p>

  <h3 style="color: #2563eb; font-size: 18px;">📌 주요 산식 및 승인 필수 조건</h3>
  <ul>
    <li><strong>법정 월 소정근로시간:</strong> (주 40시간 + 주휴 8시간) × 365일 ÷ 7일 ÷ 12개월 = <strong>209시간</strong></li>
    <li><strong>휴업급여 산정 공식:</strong> 평균임금 × 70% (1일당 최저 보상기준 적용)</li>
    <li><strong>산재 뇌심혈관 과로 기준:</strong> 발병 전 4주간 주 64시간, 12주간 주 60시간 초과 시 업무 관련성 강함</li>
  </ul>

  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; font-size: 22px; margin-top: 40px;">2. 대법원 판례 및 부장판사·전문의 판단 지침</h2>
  <p>포괄임금 계약이라 하더라도 실제 근로시간 측정이 가능하거나 연장근로수당이 법정 기준에 미달하는 경우 해당 포괄임금 약정은 법적으로 무효가 됩니다. 또한, 출퇴근 중 발생한 사고는 통상적인 경로와 방법을 벗어나지 않았다면 100% 업무상 재해로 인정됩니다.</p>

  <!-- 하단 노무체크 AI 직통 1-Click 유입 배너 카드 -->
  <div style="margin-top: 50px; padding: 28px; background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); border-radius: 20px; color: #ffffff; box-shadow: 0 12px 30px rgba(30, 58, 138, 0.3);">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
      <span style="background: #2563eb; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold;">⚖️ 법률·의학 AI 융합 서비스</span>
      <span style="color: #94a3b8; font-size: 13px;">LaborCheck AI</span>
    </div>
    <h3 style="margin: 0 0 10px 0; font-size: 22px; color: #ffffff; font-weight: 800; line-height: 1.4;">
      내 임금·주휴수당 & 산재 보상금 3초 만에 무료 진단
    </h3>
    <p style="margin: 0 0 20px 0; color: #cbd5e1; font-size: 14px; line-height: 1.6;">
      209시간 법정 기준 정밀 급여 산식 + 부장판사 판례 DB + 산재전문의 의학적 승인 확률 분석 엔진 작동 중
    </p>
    <a href="{LABORCHECK_AI_URL}" target="_blank" style="display: inline-block; width: 100%; box-sizing: border-box; text-align: center; background: linear-gradient(135deg, #2563eb, #3b82f6); color: #ffffff; text-decoration: none; padding: 16px; border-radius: 12px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);">
      🚀 24시 AI 노무·산재 무료 정밀 진단 시작하기 →
    </a>
  </div>
</div>
"""
    return html_content

def post_via_xmlrpc(keyword_info):
    try:
        wp = Client(WP_URL, WP_USER, WP_PASS)
        post = WordPressPost()
        post.title = keyword_info["title"]
        post.content = generate_labor_post_html(keyword_info)
        post.post_status = 'publish'
        
        post_id = wp.call(NewPost(post))
        print(f"[SUCCESS] Post published via XML-RPC! Post ID: {post_id}")
        return True, f"http://43.200.245.223/?p={post_id}"
    except Exception as e:
        print(f"[ERROR] XML-RPC Publishing Error: {e}")
        return False, None

if __name__ == "__main__":
    print("[START] LaborCheck AI WordPress XML-RPC Auto Publisher Running...")
    target_kw = random.choice(LABOR_KEYWORDS)
    print(f"[TARGET] Keyword: {target_kw['title']}")
    success, post_url = post_via_xmlrpc(target_kw)
    if success:
        print(f"[COMPLETED] Published Post URL: {post_url}")
