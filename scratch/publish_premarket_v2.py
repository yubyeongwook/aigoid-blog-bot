import sys
import os
import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from publishers.blogger_publisher import publish_post

now = datetime.datetime.now()
date_str = "2026년 07월 29일"
weekday_str = "수"
title = "2026년 07월 29일 수요일 장전 8:50 — 반도체 폭락 속 실적·방어주 반직관적 기회 단타·스윙 픽 5선 (진입가·손절선 포함)"
labels = ["장전브리핑", "멋쟁이픽", "동시호가", "단타", "스윙", "상한가분석"]

html_content = """<div style="max-width:720px;margin:0 auto;font-family:Apple SD Gothic Neo,Malgun Gothic,sans-serif;color:#1a1a1a;line-height:1.9;padding:0 4px">

<!-- 마스트헤드 -->
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-top:5px solid #0a0a0a;border-bottom:2px solid #0a0a0a">
<tr>
  <td width="30%" style="padding:14px 0 12px;vertical-align:middle">
    <span style="font-size:10px;color:#888;line-height:1.7">PRE-MARKET 8:50<br>수요일 장전<br>픽 5선</span>
  </td>
  <td width="40%" style="padding:14px 0 12px;vertical-align:middle;text-align:center">
    <p style="font-family:Georgia,serif;font-size:22px;font-weight:700;margin:0 0 2px">멋쟁이 인사이트</p>
    <p style="font-size:9px;letter-spacing:0.16em;color:#888;margin:0">SMART MONEY INTELLIGENCE</p>
  </td>
  <td width="30%" style="padding:14px 0 12px;vertical-align:middle;text-align:right">
    <span style="font-size:10px;color:#888;line-height:1.7">2026년 07월 29일<br>장 시작 전 전략<br>손절선 필수</span>
  </td>
</tr>
</table>
<div style="background:#0a0a0a;padding:6px 16px">
  <span style="font-size:10px;color:#ccc">나스닥 -0.22% · S&P500 +0.21% · 필라델피아반도체 -4.49% · 외국인 순매도 -4조9,914억 · 원달러 1,462.5원</span>
</div>

<!-- 수치 대시보드 8칸 -->
<table width="100%" cellpadding="0" cellspacing="1" style="border-collapse:separate;border-spacing:1px;background:#111">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">나스닥</p>
    <p style="font-size:14px;font-weight:700;color:#ef4444;margin:0 0 1px;font-family:Georgia,serif">-0.22%</p>
    <p style="font-size:10px;color:#aaa;margin:0">24,876.91pt</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">S&P500</p>
    <p style="font-size:14px;font-weight:700;color:#4ade80;margin:0 0 1px;font-family:Georgia,serif">+0.21%</p>
    <p style="font-size:10px;color:#aaa;margin:0">7,428.78pt</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">필라델피아반도체</p>
    <p style="font-size:14px;font-weight:700;color:#ef4444;margin:0 0 1px;font-family:Georgia,serif">-4.49%</p>
    <p style="font-size:10px;color:#aaa;margin:0">11,035.68pt</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">외국인 수급</p>
    <p style="font-size:14px;font-weight:700;color:#ef4444;margin:0 0 1px;font-family:Georgia,serif">-49,914억</p>
    <p style="font-size:10px;color:#aaa;margin:0">순매도</p>
  </td>
</tr>
</table>
<table width="100%" cellpadding="0" cellspacing="1" style="border-collapse:separate;border-spacing:1px;background:#111;margin:1px 0 0">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">코스피 전일</p>
    <p style="font-size:12px;font-weight:700;color:#ef4444;margin:0 0 1px">-10.84%</p>
    <p style="font-size:10px;color:#aaa;margin:0">6,023.66pt</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">코스닥 전일</p>
    <p style="font-size:12px;font-weight:700;color:#ef4444;margin:0 0 1px">-7.72%</p>
    <p style="font-size:10px;color:#aaa;margin:0">705.85pt</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">어제 상한가</p>
    <p style="font-size:12px;font-weight:700;color:#4ade80;margin:0 0 1px">5종목</p>
    <p style="font-size:10px;color:#aaa;margin:0">핵심 앤씨앤·바이오인프라</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">오늘 핵심 이벤트</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">FOMC & 빅테크</p>
    <p style="font-size:10px;color:#aaa;margin:0">실적 대기 관망세</p>
  </td>
</tr>
</table>
<p style="font-size:11px;color:#888;padding:6px 0 16px;border-bottom:1px solid #e8e5df">
출처 명시: KRX 한국거래소 (2026.07.28 마감), 연합뉴스, 뉴스핌, 네이버 증권 08:30 KST 기준
</p>

<!-- 히어로 이미지 -->
<img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900&auto=format&fit=crop&q=80"
alt="2026년 07월 29일 장전 브리핑 상한가 단타 스윙 픽 멋쟁이 인사이트"
style="width:100%;height:220px;object-fit:cover;border-radius:10px;display:block;margin:16px 0 8px">

<!-- 헤드라인 -->
<div style="padding:0 0 16px;border-bottom:2px solid #0a0a0a">
<p style="font-size:11px;letter-spacing:0.15em;color:#1a7a4a;margin:0 0 6px">PRE-MARKET 8:50 · 2026년 07월 29일 수요일 · 픽 5선 · 장 시작 전 전략</p>
<h1 style="font-family:Georgia,serif;font-size:24px;font-weight:700;line-height:1.2;margin:0 0 10px;letter-spacing:-0.02em">
어제 반도체 폭락과 5조원 외국인 매도가 몰아쳤는데<br>
오늘 실적 흑자전환·경기방어 섹터에서 반직관적 기회가 열린다<br>
— 단타·스윙 픽 5선
</h1>
<p style="font-size:14px;color:#444;line-height:1.85;margin:0;border-left:4px solid #1a7a4a;padding-left:14px">
전일 반도체발 지수 폭락 이후 미 증시는 필라델피아 반도체 약세(-4.49%) 속 다우·S&P500 실적 우량주가 방어했습니다.<br>
한국 시장은 장 초반 동시호가 반등 모멘텀과 개별 실적 흑자전환·바이오·경기방어 섹터 수급 집중이 예상됩니다.<br>
9시 10분 외국인 동시호가 수급과 시초가 갭업 10분 관망 원칙을 철저히 지키며 5개 픽으로 전술 대응합니다.
</p>
</div>

<!-- 픽 섹션 -->
<div style="padding:16px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 6px">오늘 멋쟁이 픽 5선 — 장 시작 전 최종 전략</p>
<p style="font-size:12px;color:#888;margin:0 0 12px">투자 권유가 아닙니다. 모든 수치는 어제 종가 기준 검증했습니다. 손절선 필수.</p>

<!-- 픽 A — 단타 -->
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:#0a0a0a;padding:9px 14px;display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">A · 단타 — 2분기 흑자전환 모멘텀 & 상한가 수급</span>
  <span style="color:#4ade80;font-size:11px;">★★★★★</span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:15px;font-weight:700;margin:0 0 3px">앤씨앤 (092600)</p>
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">어제 2분기 영업이익 흑자 전환 공시와 함께 강력한 매수 잔량으로 상한가(2,730원)를 기록. 시장 폭락장 속 독보적 턴어라운드 재료 보유.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;background:#f5f5f5;padding:8px;border-radius:4px;">
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">진입가</div>
      <div style="font-size:14px;font-weight:700;color:#1a3a6b;">2,720원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">손절선</div>
      <div style="font-size:14px;font-weight:700;color:#ef4444;">2,590원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 1</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,910원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 2</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">3,080원</div>
    </div>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:6px 0 0">⚠️ 상한가 이튿날 갭상승 후 시초 10분 내 차익실현 음봉 유의. 시초가 추격 매수 금지, 눌림목 공략.</p>
</div>
</div>

<!-- 픽 B — 단타 -->
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:#0a0a0a;padding:9px 14px;display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">B · 단타 — CRO 흑자전환 & 실적 수급 집중</span>
  <span style="color:#4ade80;font-size:11px;">★★★★☆</span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:15px;font-weight:700;margin:0 0 3px">바이오인프라 (270250)</p>
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">2분기 실적 흑자 달성에 따른 상한가(2,645원) 마감. 바이오 CRO 실적 개선 모멘텀이 시장 하락세와 차별화된 수급 형성.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;background:#f5f5f5;padding:8px;border-radius:4px;">
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">진입가</div>
      <div style="font-size:14px;font-weight:700;color:#1a3a6b;">2,625원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">손절선</div>
      <div style="font-size:14px;font-weight:700;color:#ef4444;">2,500원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 1</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,820원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 2</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,980원</div>
    </div>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:6px 0 0">⚠️ 개장 직후 단기 기관 매도세 출회 시 손절선 2,500원 엄수 필수.</p>
</div>
</div>

<!-- 픽 C — 단타 -->
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:#0a0a0a;padding:9px 14px;display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">C · 단타 — 바이오 섹터 반사이익 & 거래량 분출</span>
  <span style="color:#4ade80;font-size:11px;">★★★★☆</span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:15px;font-weight:700;margin:0 0 3px">셀리드 (299660)</p>
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">어제 대량 거래량과 함께 급등세(1,777원 마감). IT·반도체 이탈 자금이 바이오 신약·임상 모멘텀주로 순환매 유입되는 구간.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;background:#f5f5f5;padding:8px;border-radius:4px;">
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">진입가</div>
      <div style="font-size:14px;font-weight:700;color:#1a3a6b;">1,760원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">손절선</div>
      <div style="font-size:14px;font-weight:700;color:#ef4444;">1,680원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 1</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">1,890원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 2</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,010원</div>
    </div>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:6px 0 0">⚠️ 변동성이 둔화되거나 거래 감소 시 과감히 스캘핑 이탈 조치.</p>
</div>
</div>

<!-- 픽 D — 스윙 -->
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:#0a0a0a;padding:9px 14px;display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">D · 스윙 — 바닥권 하반경직성 & 기술적 돌파</span>
  <span style="color:#4ade80;font-size:11px;">★★★★☆</span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:15px;font-weight:700;margin:0 0 3px">포톤 (042290)</p>
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">전일 지수 붕괴 시에도 견조한 하반경직성과 함께 1,785원 마감. 바닥권 기술적 패턴 돌파 후 3~5일 스윙 시세 유효.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;background:#f5f5f5;padding:8px;border-radius:4px;">
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">진입가</div>
      <div style="font-size:14px;font-weight:700;color:#1a3a6b;">1,770원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">손절선</div>
      <div style="font-size:14px;font-weight:700;color:#ef4444;">1,690원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 1</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">1,900원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 2</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,030원</div>
    </div>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:6px 0 0">⚠️ 스윙 관점이므로 시장 전반의 투매 재발 시 분할 대응 필수.</p>
</div>
</div>

<!-- 픽 E — 스윙 -->
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:#0a0a0a;padding:9px 14px;display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">E · 스윙 — 미 증시 경기방어주 호실적 수혜</span>
  <span style="color:#4ade80;font-size:11px;">★★★★☆</span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:15px;font-weight:700;margin:0 0 3px">CJ씨푸드 (016450)</p>
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">미 증시 코카콜라 등 음료/식품 경기방어주 상승 기조 연동. 하락장에서 내수/식품 경기방어주 수급 방어벽 형성 (2,015원 마감).</p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;background:#f5f5f5;padding:8px;border-radius:4px;">
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">진입가</div>
      <div style="font-size:14px;font-weight:700;color:#1a3a6b;">2,000원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">손절선</div>
      <div style="font-size:14px;font-weight:700;color:#ef4444;">1,910원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 1</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,140원</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 2</div>
      <div style="font-size:14px;font-weight:700;color:#4ade80;">2,260원</div>
    </div>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:6px 0 0">⚠️ 지수 반등 시 방어주 자금이 반도체/IT로 재이동할 수 있어 목표가 달성 시 익절 처리.</p>
</div>
</div>

<!-- 오늘 피할 것 -->
<div style="background:#fff5f5;border:1.5px solid #ef4444;border-radius:6px;padding:12px 14px;margin:10px 0 0">
<p style="font-size:12px;font-weight:700;color:#c0392b;margin:0 0 6px">⛔ 오늘 절대 피할 것</p>
<p style="font-size:13px;color:#2c2c2c;line-height:1.8;margin:0">
삼성전자 & SK하이닉스 — 미 필라델피아 반도체(-4.49%) 및 마이크론(-8.9%) 급락에 따른 외국인 매도 지속 여파 관망 필수.<br>
CJ씨푸드1우 & 진흥기업2우B — 관리종목 및 우선주 고변동성 리스크로 추격 매수 엄금.<br>
레버리지 ETF 및 신용 융자 매수 — 지수 변동성 구간에서 반대매매 위험 극대화.<br>
갭업 시초가 추격 — 상한가 다음날 10분 관망 필수
</p>
</div>
</div>

<!-- 해외 이슈 → 한국 영향 -->
<div style="padding:16px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 12px">I · 어젯밤 해외 이슈 → 한국 영향</p>

<p style="font-size:13px;line-height:1.8;margin:0 0 6px"><strong>1. 미 반도체지수 급락(-4.49%) & AI 수익성 우려:</strong> 마이크론(-8.9%), AMD(-8.2%) 급락으로 국산 HBM/반도체 대형주 장 초반 하방 압력.</p>
<p style="font-size:13px;line-height:1.8;margin:0 0 6px"><strong>2. 다우 우량주 호실적 & FOMC 금리 동결 기대:</strong> 코카콜라 등 소비재 호실적으로 S&P500 방어, 한국 내수 경기방어주로 자금 이동 유도.</p>
<p style="font-size:13px;line-height:1.8;margin:0 0 12px"><strong>3. 원/달러 환율 안정세(1,462원 → 1,446원대 진입):</strong> 달러 매도 물량 및 수급 안정화 기대로 국내 외국인 매도 폭 감소 가능성.</p>

<p style="font-size:12px;color:#444;margin:0">수혜: 바이오/CRO, 개별 흑자전환 실적주, 음식료/경기방어주<br>
피해: 대형 반도체, 고부채 주식, 레버리지 ETF</p>
</div>

<!-- 어제 상한가 분석 -->
<div style="padding:16px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 12px">II · 어제 상한가 — 오늘 연속 가능한가</p>

<p style="font-size:13px;line-height:1.8;margin:0 0 6px"><strong>앤씨앤:</strong> 2분기 영업이익 흑자전환 재료 유효 · 연속 가능성 <strong>[높음]</strong></p>
<p style="font-size:13px;line-height:1.8;margin:0 0 6px"><strong>바이오인프라:</strong> CRO 흑자전환 및 매수세 유입 · 연속 가능성 <strong>[높음]</strong></p>
<p style="font-size:13px;line-height:1.8;margin:0 0 6px"><strong>진흥기업우B / CJ씨푸드1우:</strong> 우선주 품귀 현상 단기 수급 · 연속 가능성 <strong>[낮음] (관망)</strong></p>

<p style="font-size:12px;color:#c0392b;margin:6px 0 0">갭업 시 전략: 시초가 매수 금지 · 10분 관망 · 눌림목 진입</p>
</div>

<!-- 멋쟁이 결론 -->
<div style="background:#0a0a0a;padding:16px 20px;margin:16px 0 4px">
<p style="font-size:9px;letter-spacing:0.18em;color:#f0c040;margin:0 0 8px">멋쟁이의 결론</p>
<p style="color:#e2e2e2;font-size:14px;line-height:1.9;margin:0 0 8px">어제의 10% 급락은 반도체 수급 쏠림과 레버리지 청산이 만든 극단적 발작이었습니다. 미국 증시에서 반도체는 조정을 받았으나 일반 우량주와 방어주는 반등했습니다. 국내 시장도 대형 반도체 충격 뒤 개별 흑자전환 종목과 바이오·방어주 섹터에서 강한 반등 시도가 나타날 것입니다.</p>
<p style="color:#e2e2e2;font-size:14px;line-height:1.9;margin:0">오전 9시 10분 외국인 수급 방향이 오늘의 모든 것을 결정한다.</p>
</div>

<!-- 투자 고지 -->
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:2px solid #c0392b;margin:12px 0 0">
<tr><td style="background:#c0392b;padding:8px 14px">
<p style="font-size:11px;font-weight:700;color:#fff;margin:0">투자 위험 고지</p>
</td></tr>
<tr><td style="background:#fff8f7;padding:10px 14px">
<p style="font-size:12px;color:#5a1a1a;line-height:1.8;margin:0">
본 글은 투자 정보 제공 목적이며 특정 종목의 매수·매도를 권유하지 않습니다.
모든 픽에 반드시 손절선을 설정하세요.
<strong>모든 투자의 최종 판단과 책임은 전적으로 투자자 본인에게 있습니다.</strong>
</p>
</td></tr>
</table>

<!-- 출처 푸터 -->
<p style="background:#f5f4f0;border-radius:6px;padding:8px 12px;font-size:10px;color:#999;line-height:1.7;margin:8px 0 0">
확정 수치: KRX 한국거래소 (2026.07.28 종가 기준), 연합뉴스, 뉴스핌, 네이버 증권 2026.07.29 08:30 KST 기준
</p>

</div>"""

def main():
    print("Publishing Premarket Briefing v2 to Blogger...")
    result = publish_post(title=title, html_content=html_content, labels=labels, draft=False)
    print("Result:", result)

if __name__ == "__main__":
    main()
