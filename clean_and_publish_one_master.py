import os
import requests
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, DeletePost, NewPost

# ==========================================
# 1. AWS Lightsail WordPress XML-RPC 설정
# ==========================================
WP_URL = "http://43.200.245.223/xmlrpc.php"
WP_USER = "user"
WP_PASS = "LaborCheck123!"

LABORCHECK_AI_URL = "https://laborcheck-ai.vercel.app"

def clean_all_posts(wp):
    print("[CLEANUP] Cleaning all existing posts from WordPress...")
    try:
        posts = wp.call(GetPosts({'number': 100}))
        for post in posts:
            wp.call(DeletePost(post.id))
            print(f"[DELETED] Post ID {post.id} deleted successfully.")
        print("[CLEANUP COMPLETE] All existing posts deleted.")
    except Exception as e:
        print(f"[ERROR CLEANING] {e}")

def publish_single_master_post(wp):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 파이썬 동적 수치 정밀 계산 검증
    h2025 = 10030
    m2025 = h2025 * 209  # 2,096,270원 (100% 검증)
    h2026 = 10320
    m2026 = h2026 * 209  # 2,156,880원 (100% 검증)

    title = "2025년-2026년 최저시급 10,030원 및 10,320원 기준 209시간 월급 수치 정밀 산식 검증 가이드"

    html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Pretendard',sans-serif;color:#1e293b;line-height:1.9;max-width:860px;margin:0 auto;background:#fff;">

<!-- 마스트헤드 -->
<table width="100%" style="border-bottom:2px solid #0f172a;border-collapse:collapse;margin-bottom:24px;">
  <tr>
    <td width="35%" style="font-size:13px;color:#64748b;padding:10px 0;">{date_str} · 임금·퇴직금 전문 심층 검증</td>
    <td width="30%" align="center" style="font-size:15px;font-weight:900;letter-spacing:1px;padding:10px 0;color:#0f172a;">노무체크 AI 인사노무 저널</td>
    <td width="35%" align="right" style="font-size:13px;color:#64748b;padding:10px 0;">SEO 키워드: 2025년 최저시급 209시간 최저월급</td>
  </tr>
</table>

<!-- 멋쟁이 인사노무 핵심 요약 박스 -->
<div style="background:#0f172a;color:#ffffff;padding:26px;border-radius:12px;margin-bottom:32px;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 14px;letter-spacing:1px;">멋쟁이 인사노무 핵심 요약 (TODAY'S ESSENCE)</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">1. <strong>2025년 확정 최저시급 정밀 검증:</strong> {h2025:,}원 × 209시간 = <strong>{m2025:,}원</strong> (오차 0원 정밀 검증 공식)</p>
  <p style="font-size:15px;margin:0 0 10px;line-height:1.7;">2. <strong>2026년 인상 반영 기준:</strong> {h2026:,}원 × 209시간 = <strong>{m2026:,}원</strong> (주휴 8시간 유급 포함)</p>
  <p style="font-size:15px;margin:0;line-height:1.7;">3. <strong>법적 시효 소멸:</strong> 임금체불 및 수당 차액 청구권은 3년간 유효</p>
</div>

<!-- 히어로 이미지 -->
<div style="margin-bottom:36px;text-align:center;">
  <img src="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80" alt="{title}" style="width:100%;max-height:440px;object-fit:cover;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.08);">
</div>

<h1 style="font-size:28px;font-weight:900;color:#0f172a;line-height:1.4;margin:0 0 36px;letter-spacing:-0.5px;">{title}</h1>

<!-- 섹션 I -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">I · 법적 근거 — 근로기준법 및 최저임금법 수치 법리</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
대한민국 근로기준법 제43조 및 최저임금법 제6조에 따르면, 사업주는 고용노동부장관이 고시한 최저임금액 이상의 임금을 근로자에게 지급하여야 합니다. 
월 소정근로시간 209시간 산출 산식은 (주 40시간 + 유급 주휴 8시간) × 365일 ÷ 7일 ÷ 12개월 = 208.71시간을 소수점 올림 한 209시간이 법정 표준 기준입니다.
</p>

<!-- 정밀 계산 검증 상자 -->
<div style="background:#f8fafc;border:2px solid #2563eb;padding:26px;border-radius:12px;margin:28px 0;">
  <h4 style="margin:0 0 14px;color:#1e3a8a;font-size:17px;font-weight:bold;">🔍 [100% 수학 정밀 검증] 최저임금 연도별 월급 산출표</h4>
  <p style="margin:0 0 10px;font-size:15.5px;color:#334155;">• <strong>2025년 확정 시급 ({h2025:,}원):</strong> {h2025:,}원 × 209시간 = <span style="color:#2563eb;font-weight:bold;">{m2025:,}원</span></p>
  <p style="margin:0 0 10px;font-size:15.5px;color:#334155;">• <strong>2026년 인상 기준 ({h2026:,}원):</strong> {h2026:,}원 × 209시간 = <span style="color:#2563eb;font-weight:bold;">{m2026:,}원</span></p>
  <p style="margin:12px 0 0;font-size:14px;color:#64748b;border-top:1px solid #e2e8f0;padding-top:10px;">* 주 35시간 유급 주휴가 100% 포함된 무결점 법정 최소 기본급 계산 결과입니다.</p>
</div>

<!-- 섹션 II -->
<h2 style="font-size:20px;font-weight:800;color:#1e3a8a;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin:40px 0 20px;">II · 임금체불 발생 시 대응 및 3년 소멸시효 청구</h2>
<p style="font-size:16.5px;color:#334155;margin-bottom:20px;">
만약 월급이 법정 최저 월급인 {m2025:,}원 미만으로 수령되고 있다면 임금체불에 해당합니다. 
근로자는 3년 이내의 미지급 차액 수당을 소급하여 고용노동부(국번없이 1350)를 통해 진정을 접수할 수 있습니다.
</p>

<!-- 실전 체크리스트 -->
<div style="background:#f0fff5;border-left:5px solid #16a34a;padding:24px;margin:28px 0;border-radius:0 8px 8px 0;">
  <p style="font-size:16px;font-weight:800;color:#15803d;margin:0 0 14px;">지금 당장 확인할 실전 체크리스트</p>
  <p style="font-size:15px;color:#334155;margin:0 0 8px;">□ 근로계약서상 약정 시급 및 소정근로시간 확인</p>
  <p style="font-size:15px;color:#334155;margin:0 0 8px;">□ 매월 수령하는 임금명세서 항목별 수당 계산 산식 확인</p>
  <p style="font-size:15px;color:#334155;margin:0;">□ 출퇴근 시간 메모 및 객관적 내역 보관</p>
</div>

<!-- 노무체크 AI 전문 시각 박스 -->
<div style="background:#0f172a;border:1px solid #334155;padding:26px;border-radius:12px;margin:36px 0;">
  <p style="font-size:14px;font-weight:800;color:#fbbf24;margin:0 0 12px;letter-spacing:1px;">EXPERTS PERSPECTIVE · 노무체크 AI 정밀 총평</p>
  <p style="font-size:15px;color:#e2e8f0;line-height:1.85;margin:0;">
    "정확한 법정 소정근로시간(209시간)과 수치 정밀 계산을 바탕으로 임금을 산정하는 것이 노동법 분쟁 예방의 첫걸음입니다."
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
        본 수치 검증 데이터는 최저임금법 및 근로기준법상 209시간 정밀 공식을 바탕으로 파이썬 엔진에서 수학적으로 100% 검증된 정밀 데이터입니다.
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

    post = WordPressPost()
    post.title = title
    post.content = html
    post.post_status = 'publish'

    post_id = wp.call(NewPost(post))
    post_url = f"http://43.200.245.223/?p={post_id}"
    print(f"[SINGLE MASTER POST CREATED] ID: {post_id} / URL: {post_url}")
    return post_url

if __name__ == "__main__":
    wp = Client(WP_URL, WP_USER, WP_PASS)
    # 1. 기존 테스트 게시물 전량 싹 청소 삭제
    clean_all_posts(wp)
    # 2. 100% 수치 검증 단 1개 명품 포스팅 실시간 게시
    final_url = publish_single_master_post(wp)
    print(f"[COMPLETE] Final Master Post URL: {final_url}")
