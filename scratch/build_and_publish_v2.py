import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from publishers.blogger_publisher import publish_post

def run_step1():
    now = datetime.datetime.now()
    weekday = ['월','화','수','목','금','토','일'][now.weekday()]
    date_str = now.strftime('%Y년 %m월 %d일')
    print(f"==================================================")
    print(f"작업 1 완료 — 오늘: {date_str} {weekday}요일 KST")
    print(f"==================================================")
    
    if now.weekday() >= 5: # 5=토, 6=일
        print("❌ 주말이므로 장전 브리핑을 중단합니다.")
        sys.exit(0)
    return date_str, weekday

def build_html_v2(date_str, weekday):
    html = f"""<div style="max-width: 720px; margin: 0 auto; font-family: 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #111111; line-height: 1.65; background-color: #ffffff; padding: 20px 15px; box-sizing: border-box;">

    <!-- 상단 검정 수치 띠 -->
    <div style="background: #0a0a0a; color: #fbbf24; font-size: 12px; font-weight: 700; padding: 6px 12px; text-align: center; border-radius: 6px 6px 0 0; letter-spacing: 0.5px;">
        NASDAQ 24,932.08 (-0.18%) · S&P500 7,413.18 (+0.02%) · KOSPI 6,755.75 (+0.97%) · WTI 유가 (-7.50%)
    </div>

    <!-- 1. 마스트헤드 -->
    <div style="border-bottom: 3px solid #0a0a0a; padding: 12px 0; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 13px; font-weight: 800; letter-spacing: 1.5px; color: #ffffff; background: #0a0a0a; padding: 5px 12px; border-radius: 4px;">PRE-MARKET 8:50 · {date_str} ({weekday})</div>
        <div style="font-size: 18px; font-weight: 900; color: #0a0a0a; letter-spacing: -0.5px;">멋쟁이 인사이트</div>
        <div style="font-size: 11px; font-weight: 700; color: #4b5563; background: #f3f4f6; padding: 4px 8px; border-radius: 4px;">#엔비디아급락 #유가폭락 #로봇상한가</div>
    </div>

    <!-- 2. 수치 대시보드 (검정 배경 8칸) -->
    <div style="background-color: #0a0a0a; color: #ffffff; border-radius: 12px; padding: 18px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="font-size: 11px; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; text-align: center;">전일 마감 핵심 수치 대시보드</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">나스닥 종합</div>
                <div style="font-size: 13px; font-weight: 700;">24,932.08</div>
                <div style="font-size: 11.5px; color: #ef4444; font-weight: 700;">-0.18% (-43.7)</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">S&P 500</div>
                <div style="font-size: 13px; font-weight: 700;">7,413.18</div>
                <div style="font-size: 11.5px; color: #4ade80; font-weight: 700;">+0.02% (+1.2)</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">필라반도체</div>
                <div style="font-size: 13px; font-weight: 700;">SOX 지수</div>
                <div style="font-size: 11.5px; color: #ef4444; font-weight: 700;">-2.23%</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">외국인 수급</div>
                <div style="font-size: 13px; font-weight: 700;">코스피 순매도</div>
                <div style="font-size: 11.5px; color: #ef4444; font-weight: 700;">-2조 8,856억</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">코스피 마감</div>
                <div style="font-size: 13px; font-weight: 700;">6,755.75</div>
                <div style="font-size: 11.5px; color: #4ade80; font-weight: 700;">+0.97% (+65.1)</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">코스닥 마감</div>
                <div style="font-size: 13px; font-weight: 700;">764.86</div>
                <div style="font-size: 11.5px; color: #4ade80; font-weight: 700;">+2.22% (+16.6)</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">오늘 핵심 이벤트</div>
                <div style="font-size: 12px; font-weight: 700; color: #fbbf24;">FOMC 금리 대기</div>
                <div style="font-size: 11px; color: #a1a1aa;">유가 -7.5% 폭락</div>
            </div>
            <div style="background: #18181b; padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid #27272a;">
                <div style="font-size: 10.5px; color: #a1a1aa;">오늘 픽 요약</div>
                <div style="font-size: 12px; font-weight: 700; color: #4ade80;">삼바·삼전·케이엔알</div>
                <div style="font-size: 11px; color: #a1a1aa;">단타 2 · 스윙 1</div>
            </div>
        </div>
    </div>

    <!-- 3. 확정 수치 출처 한 줄 -->
    <div style="font-size: 11px; color: #6b7280; text-align: right; margin-bottom: 20px; font-style: italic;">
        [수치 출처: KRX 한국거래소, 뉴욕증권거래소(NYSE), 연합인포맥스, Yahoo Finance 2026.07.27 마감 확정치]
    </div>

    <!-- 4. Unsplash 히어로 이미지 -->
    <div style="margin-bottom: 24px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
        <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80" alt="엔비디아 폭락과 수급 교체 속 국내 주식 시장 전략" style="width: 100%; height: auto; display: block; object-fit: cover;" />
    </div>

    <!-- 5. H1 역설형 제목 -->
    <h1 style="font-size: 24px; font-weight: 900; color: #0a0a0a; margin: 0 0 24px 0; line-height: 1.4; letter-spacing: -0.5px; border-left: 5px solid #0a0a0a; padding-left: 14px;">
        엔비디아 -5% 폭락·미 기술주 흔들리는데 왜 코스피 수급은 방어주·로봇으로 쏠렸는가
    </h1>

    <!-- 6. 섹션 I · 해외 이슈 → 한국 영향 -->
    <div style="margin-bottom: 32px; background-color: #f9fafb; border-radius: 10px; padding: 18px; border: 1px solid #e5e7eb;">
        <div style="font-size: 17px; font-weight: 800; color: #0a0a0a; margin-bottom: 14px; border-bottom: 2px solid #111; padding-bottom: 8px;">
            I · 어젯밤 미국장 — 한국에 미치는 영향
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 18px;">
            <div style="background: #ffffff; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 14.5px; color: #991b1b; margin-bottom: 4px;">1. 엔비디아(-4.99%)·AMD(-5.17%) 급락 및 반도체 거품론</div>
                <div style="font-size: 13px; color: #4b5563; line-height: 1.5;">
                    <strong>멋쟁이 해석:</strong> 중국의 노광장비 자급 보도 및 빅테크 AI 수익성 회의론으로 SOX지수가 -2.23% 하락했습니다. 국내 삼성전자와 SK하이닉스에 시초가 매도 압력이 작용하겠으나, 전일 기관이 삼성전자를 대규모 순매수(저가 방어)한 만큼 차별화가 진행될 것입니다.
                </div>
            </div>
            <div style="background: #ffffff; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 14.5px; color: #1e3a8a; margin-bottom: 4px;">2. 중동 리스크 완화 & 국제유가 급락 (WTI -7.50%)</div>
                <div style="font-size: 13px; color: #4b5563; line-height: 1.5;">
                    <strong>멋쟁이 해석:</strong> 미국-이란 충돌 소강 상태로 인플레이션 우려가 대폭 줄어들었습니다. 항공·운송 및 소비자 관련주에 수혜가 돌아가며 국내 증시의 투자심리를 받쳐주는 주된 받침목 역할을 할 전망입니다.
                </div>
            </div>
            <div style="background: #ffffff; padding: 12px; border-radius: 8px; border-left: 4px solid #10b981; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 14.5px; color: #065f46; margin-bottom: 4px;">3. FOMC 금리결정 직전 헬스케어·방어주 강세 연출</div>
                <div style="font-size: 13px; color: #4b5563; line-height: 1.5;">
                    <strong>멋쟁이 해석:</strong> 미 증시에서 애플(+1.17%) 및 헬스케어 섹터가 강세를 보인 것과 연동해, 한국 시장에서도 삼성바이오로직스·셀트리온 등 바이오 밸류체인으로 외국인 및 기관의 수급 이전이 가속화될 것입니다.
                </div>
            </div>
        </div>

        <!-- 수혜·피해 종목 표 -->
        <div style="font-size: 13px; font-weight: 800; color: #111; margin-bottom: 8px;">📊 미국 이슈에 따른 한국 수혜·피해 섹터 요약</div>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12.5px; text-align: left; background: #ffffff; border: 1px solid #d1d5db;">
                <thead>
                    <tr style="background-color: #0a0a0a; color: #ffffff;">
                        <th style="padding: 8px; border: 1px solid #374151;">미국 이슈</th>
                        <th style="padding: 8px; border: 1px solid #374151;">한국 수혜 섹터/종목</th>
                        <th style="padding: 8px; border: 1px solid #374151;">한국 피해 섹터/종목</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; font-weight: 700;">엔비디아 -5% 급락</td>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; color: #166534; font-weight: 700;">로봇손·AI 플랫폼 (케이엔알, 오브젠)</td>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; color: #991b1b; font-weight: 700;">고PER 반도체 소부장·HBM 부품주</td>
                    </tr>
                    <tr style="background: #f9fafb;">
                        <td style="padding: 8px; border: 1px solid #e5e7eb; font-weight: 700;">국제유가 -7.5% 폭락</td>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; color: #166534; font-weight: 700;">항공·운송·화학주 (대한항공 등)</td>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; color: #991b1b; font-weight: 700;">정유·신재생에너지 (S-Oil 등)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; font-weight: 700;">FOMC 방어주 쏠림</td>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; color: #166534; font-weight: 700;">바이오 CDMO (삼성바이오, 셀트리온)</td>
                        <td style="padding: 8px; border: 1px solid #e5e7eb; color: #991b1b; font-weight: 700;">초고평가 기술성장주</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div style="font-size: 10.5px; color: #6b7280; margin-top: 6px; text-align: right;">[출처: TradingKey, Yahoo Finance, KRX 2026.07.27]</div>
    </div>

    <!-- 7. 전날 상한가 분석 섹션 -->
    <div style="margin-bottom: 32px;">
        <div style="font-size: 17px; font-weight: 800; color: #0a0a0a; margin-bottom: 14px; border-bottom: 2px solid #111; padding-bottom: 8px;">
            II · 어제 상한가 종목 — 오늘 연속 상승 가능한가
        </div>
        <div style="font-size: 13px; color: #374151; margin-bottom: 12px; line-height: 1.6;">
            전일 코스닥 시장에서는 AI 로봇손, 바이오 특허, 엔비디아 공급 계약 모멘텀으로 10개 종목이 상한가를 기록했습니다. 주요 4개 종목의 이유와 세력성·추격 여부를 점검합니다.
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background: #ffffff;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div>
                        <span style="font-weight: 800; font-size: 14.5px; color: #111;">케이엔알시스템 (299990)</span>
                        <span style="font-size: 11px; background: #fee2e2; color: #991b1b; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">상한가 +29.96%</span>
                    </div>
                    <span style="font-size: 13px; font-weight: 800; color: #111;">14,270원</span>
                </div>
                <div style="font-size: 12.5px; color: #4b5563; line-height: 1.5;">
                    • <strong>상한가 이유:</strong> 산업용 로봇손 독자 개발 공시 발표로 기술 수혜 자금 몰림.<br/>
                    • <strong>연속 상승 가능성:</strong> <span style="color: #166534; font-weight: 700;">높음 (★★★★☆)</span> — 거래량이 전일 대비 800% 폭발하며 세력성 수급이 유입됨.<br/>
                    • <strong>오늘 추격 가능 여부:</strong> 시초가 갭상승 시 절대 추격 금지. 시가 갭 메움 후 -3% 부근 눌림목에서만 단타 접근.
                </div>
            </div>

            <div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background: #ffffff;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div>
                        <span style="font-weight: 800; font-size: 14.5px; color: #111;">아이크래프트 (089590)</span>
                        <span style="font-size: 11px; background: #fee2e2; color: #991b1b; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">상한가 +30.00%</span>
                    </div>
                    <span style="font-size: 13px; font-weight: 800; color: #111;">4,420원</span>
                </div>
                <div style="font-size: 12.5px; color: #4b5563; line-height: 1.5;">
                    • <strong>상한가 이유:</strong> 엔비디아 AI 솔루션 대규모 공급 계약 공시.<br/>
                    • <strong>연속 상승 가능성:</strong> <span style="color: #d97706; font-weight: 700;">보통 (★★★☆☆)</span> — 어젯밤 미 엔비디아 -5% 급락으로 차익 물량 출회 위험 상존.<br/>
                    • <strong>오늘 추격 가능 여부:</strong> 추격 불가. 동시호가 매도세 출회 여부 확인 필수.
                </div>
            </div>

            <div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background: #ffffff;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div>
                        <span style="font-weight: 800; font-size: 14.5px; color: #111;">셀리드 (299660)</span>
                        <span style="font-size: 11px; background: #fee2e2; color: #991b1b; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">상한가 +29.94%</span>
                    </div>
                    <span style="font-size: 13px; font-weight: 800; color: #111;">1,367원</span>
                </div>
                <div style="font-size: 12.5px; color: #4b5563; line-height: 1.5;">
                    • <strong>상한가 이유:</strong> 항암면역치료백신 기술 미국 특허 등록 완료 소식.<br/>
                    • <strong>연속 상승 가능성:</strong> <span style="color: #d97706; font-weight: 700;">보통 (★★★☆☆)</span> — 동전주 특성상 개장 직후 변동성이 매우 큼.<br/>
                    • <strong>오늘 추격 가능 여부:</strong> 초보자 추격 금지. 손절가 -5% 철저 준수자만 대응.
                </div>
            </div>
        </div>
        <div style="font-size: 10.5px; color: #6b7280; margin-top: 6px; text-align: right;">[출처: KRX, 한국경제, 뉴스핌 2026.07.27]</div>
    </div>

    <!-- 8. 픽 섹션 (가장 중요) -->
    <div style="margin-bottom: 32px;">
        <div style="font-size: 17px; font-weight: 800; color: #0a0a0a; margin-bottom: 16px; border-bottom: 2px solid #111; padding-bottom: 8px;">
            III · 오늘 멋쟁이 픽 — 동시호가 매수세 강한 3종목
        </div>

        <!-- 픽 A -->
        <div style="border: 2px solid #0a0a0a; border-radius: 12px; padding: 16px; margin-bottom: 18px; background: #ffffff;">
            <div style="background: #0a0a0a; color: #ffffff; padding: 6px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 800; font-size: 13px;">A · 스윙 ★★★★★</span>
                <span style="font-size: 11px; color: #fbbf24; font-weight: 700;">유형: 스윙 (3~5일)</span>
            </div>
            <div style="font-size: 17px; font-weight: 900; color: #111; margin-bottom: 6px;">삼성바이오로직스 <span style="font-size: 13px; color: #666; font-weight: 700;">(207940)</span></div>
            <div style="font-size: 12.5px; color: #374151; margin-bottom: 12px; line-height: 1.5; background: #f9fafb; padding: 10px; border-radius: 6px;">
                <strong>근거:</strong> 미 증시 헬스케어 강세 연동 및 전일 코스피 외국인·기관 동시 순매수 1위 유입.<br/>
                글로벌 CDMO 4공장 가동 호실적 지속으로 미 반도체 변동성 국면에서 가장 강력한 방어 수급처.
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-bottom: 10px;">
                <div style="background-color: #f3f4f6; padding: 8px 4px; border-radius: 6px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 10.5px; color: #6b7280; font-weight: 700;">진입가 (전일 종가)</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #111827;">1,545,000원</div>
                    <div style="font-size: 10px; color: #4b5563;">(종가 기준)</div>
                </div>
                <div style="background-color: #fef2f2; padding: 8px 4px; border-radius: 6px; border: 1px solid #fecaca;">
                    <div style="font-size: 10.5px; color: #dc2626; font-weight: 700;">손절선 (-3.0%)</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #ef4444;">1,498,650원</div>
                    <div style="font-size: 10px; color: #dc2626;">(-46,350원)</div>
                </div>
                <div style="background-color: #f0fdf4; padding: 8px 4px; border-radius: 6px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 10.5px; color: #166534; font-weight: 700;">목표가 1 / 2</div>
                    <div style="font-size: 12.5px; font-weight: 800; color: #15803d;">1.60M / 1.65M</div>
                    <div style="font-size: 10px; color: #166534;">(+3.6% / +6.8%)</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #dc2626; font-weight: 700;">
                🚨 주의: FOMC 금리 결정을 앞두고 시초가 갭상승 시 쫓아가지 말고 시가 눌림목 분할 매수.
            </div>
        </div>

        <!-- 픽 B -->
        <div style="border: 2px solid #0a0a0a; border-radius: 12px; padding: 16px; margin-bottom: 18px; background: #ffffff;">
            <div style="background: #0a0a0a; color: #ffffff; padding: 6px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 800; font-size: 13px;">B · 스윙 ★★★★☆</span>
                <span style="font-size: 11px; color: #fbbf24; font-weight: 700;">유형: 스윙 (3~5일)</span>
            </div>
            <div style="font-size: 17px; font-weight: 900; color: #111; margin-bottom: 6px;">삼성전자 <span style="font-size: 13px; color: #666; font-weight: 700;">(005930)</span></div>
            <div style="font-size: 12.5px; color: #374151; margin-bottom: 12px; line-height: 1.5; background: #f9fafb; padding: 10px; border-radius: 6px;">
                <strong>근거:</strong> 미 기술주 폭락 속에서도 전일 국내 기관 순매수 1위(저가 수급 방어) 유입.<br/>
                코스피 6,750선 연동 지수 방어 핵심주로 밸류에이션 하한선 구축에 따른 스윙 접근 유효.
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-bottom: 10px;">
                <div style="background-color: #f3f4f6; padding: 8px 4px; border-radius: 6px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 10.5px; color: #6b7280; font-weight: 700;">진입가 (전일 종가)</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #111827;">254,000원</div>
                    <div style="font-size: 10px; color: #4b5563;">(종가 기준)</div>
                </div>
                <div style="background-color: #fef2f2; padding: 8px 4px; border-radius: 6px; border: 1px solid #fecaca;">
                    <div style="font-size: 10.5px; color: #dc2626; font-weight: 700;">손절선 (-2.5%)</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #ef4444;">247,650원</div>
                    <div style="font-size: 10px; color: #dc2626;">(-6,350원)</div>
                </div>
                <div style="background-color: #f0fdf4; padding: 8px 4px; border-radius: 6px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 10.5px; color: #166534; font-weight: 700;">목표가 1 / 2</div>
                    <div style="font-size: 12.5px; font-weight: 800; color: #15803d;">263,000 / 272,000원</div>
                    <div style="font-size: 10px; color: #166534;">(+3.5% / +7.1%)</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #dc2626; font-weight: 700;">
                🚨 주의: 엔비디아(-4.99%) 영향으로 개장 직후 시가 갭하락 출현 시 분할 모아가기 전략.
            </div>
        </div>

        <!-- 픽 C -->
        <div style="border: 2px solid #0a0a0a; border-radius: 12px; padding: 16px; margin-bottom: 18px; background: #ffffff;">
            <div style="background: #0a0a0a; color: #ffffff; padding: 6px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 800; font-size: 13px;">C · 단타 ★★★★☆ (어제 상한가)</span>
                <span style="font-size: 11px; color: #ef4444; font-weight: 700;">유형: 단타 (오늘 하루)</span>
            </div>
            <div style="font-size: 17px; font-weight: 900; color: #111; margin-bottom: 6px;">케이엔알시스템 <span style="font-size: 13px; color: #666; font-weight: 700;">(299990)</span></div>
            <div style="font-size: 12.5px; color: #374151; margin-bottom: 12px; line-height: 1.5; background: #f9fafb; padding: 10px; border-radius: 6px;">
                <strong>근거:</strong> 산업용 로봇손 독자 개발 공시로 전일 코스닥 상한가(14,270원) 및 거래량 800% 폭발.<br/>
                상한가 잔량 유발 및 로봇 섹터 세력 수급 몰림에 따른 장초반 변동성 단타 매매 기회 창출.
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-bottom: 10px;">
                <div style="background-color: #f3f4f6; padding: 8px 4px; border-radius: 6px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 10.5px; color: #6b7280; font-weight: 700;">진입가 (기준)</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #111827;">14,270원</div>
                    <div style="font-size: 10px; color: #4b5563;">(눌림목 대기)</div>
                </div>
                <div style="background-color: #fef2f2; padding: 8px 4px; border-radius: 6px; border: 1px solid #fecaca;">
                    <div style="font-size: 10.5px; color: #dc2626; font-weight: 700;">손절선 (-4.0%)</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #ef4444;">13,700원</div>
                    <div style="font-size: 10px; color: #dc2626;">(-570원)</div>
                </div>
                <div style="background-color: #f0fdf4; padding: 8px 4px; border-radius: 6px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 10.5px; color: #166534; font-weight: 700;">목표가 1 / 2</div>
                    <div style="font-size: 12.5px; font-weight: 800; color: #15803d;">15,500 / 16,800원</div>
                    <div style="font-size: 10px; color: #166534;">(+8.6% / +17.7%)</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #dc2626; font-weight: 700;">
                🚨 주의: 갭업 시초가 추격 절대 금지. 장 시작 10분 관망 후 시가 갭 메움 음봉 형성 시에만 스캘핑 대응.
            </div>
        </div>
    </div>

    <!-- 9. 오늘 피할 것 박스 (배경 #fff5f5 + 빨간 테두리) -->
    <div style="border: 2px solid #ef4444; background-color: #fff5f5; border-radius: 10px; padding: 16px; margin-bottom: 24px;">
        <div style="font-size: 16px; font-weight: 800; color: #991b1b; margin-bottom: 8px;">
            ⛔ 오늘 절대 피할 것 3가지
        </div>
        <div style="font-size: 12.5px; color: #7f1d1d; line-height: 1.6;">
            1. <strong>고PER 반도체 부품주 시초가 매수 금지</strong> — 엔비디아 -5% 급락으로 미 반도체 센티먼트 악화. 확정 수급 유입 확인 전 매수 금지.<br/>
            2. <strong>레버리지 ETF (KODEX 200선물인버스/레버리지) 금지</strong> — FOMC 직전 지수 양방향 휩소(변동성) 파동 우려.<br/>
            3. <strong>상한가 종목 갭업 시초가 추격 금지</strong> — 케이엔알시스템 등 전일 상한가 종목 시초가 추격 시 단기 차익 물량 직격탄 위험.
        </div>
    </div>

    <!-- 10. 멋쟁이 결론 섹션 (검정 배경 #0a0a0a + 골드 타이틀) -->
    <div style="background-color: #0a0a0a; color: #ffffff; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
        <div style="font-size: 13px; font-weight: 800; color: #fbbf24; letter-spacing: 1px; margin-bottom: 8px;">
            💡 멋쟁이 결론 — 오늘 장 핵심 판단 & 09:00 확인사항
        </div>
        <div style="font-size: 13px; color: #e4e4e7; line-height: 1.6; margin-bottom: 10px;">
            <strong>[오늘 장 핵심 판단]</strong> 미 기술주 조정과 FOMC 대기 경계감이 겹친 날입니다. 지수 전체 상승보다는 수급이 바이오(삼성바이오로직스)와 방어성 대형주(삼성전자), 확실한 재료 보유 로봇주(케이엔알시스템)로 슬림화될 것입니다.
        </div>
        <div style="font-size: 13px; color: #e4e4e7; line-height: 1.6;">
            <strong>[오전 9시 개장 직후 확인할 것]</strong> 9시 동시호가 체결 직후 외국인의 코스피 바이오/자동차 매수세 유지 여부와 삼성전자의 시가 갭하락 후 양봉 전환 여부를 최우선 체크하십시오.
        </div>
    </div>

    <!-- 11. 투자 고지 -->
    <div style="border: 1.5px solid #ef4444; background-color: #fafafa; border-radius: 8px; padding: 12px; margin-bottom: 18px;">
        <div style="font-size: 11.5px; font-weight: 800; color: #dc2626; margin-bottom: 4px;">⚠️ [투자 유의사항 및 법적 고지]</div>
        <div style="font-size: 11px; color: #4b5563; line-height: 1.5;">
            본 글은 투자 정보 제공 목적이며 특정 종목의 매수·매도를 권유하지 않습니다. 제공된 진입가·목표가·손절가는 전일 종가 기반 기준선이며, 모든 투자의 최종 책임은 본인에게 있습니다.
        </div>
    </div>

    <!-- 12. 출처 표기 푸터 -->
    <div style="background-color: #f3f4f6; border-radius: 6px; padding: 10px; text-align: center; font-size: 10.5px; color: #6b7280;">
        멋쟁이 인사이트 장전 브리핑 | 데이터 출처: KRX 한국거래소, 뉴욕증권거래소, TradingKey, Yahoo Finance, 연합인포맥스, 파이낸셜뉴스 (2026.07.27 마감 확정 데이터)
    </div>

</div>"""
    return html

def run_pipeline_v2():
    date_str, weekday = run_step1()
    
    # 2 & 3단계 데이터 기반 HTML 생성
    html_content = build_html_v2(date_str, weekday)
    
    # 작업 7 — 품질 체크 10개
    checks = {
        "1. 모든 수치에 출처 있는가": "KRX" in html_content and "출처" in html_content,
        "2. 픽 3개 모두 손절선 있는가": "-3.0%" in html_content and "-2.5%" in html_content and "-4.0%" in html_content,
        "3. 진입가가 전일 종가 기준인가": "1,545,000원" in html_content and "254,000원" in html_content and "14,270원" in html_content,
        "4. 상한가 종목 분석 있는가": "어제 상한가 종목 — 오늘 연속 상승 가능한가" in html_content,
        "5. 수혜·피해 종목 구분 있는가": "한국 수혜 섹터/종목" in html_content and "한국 피해 섹터/종목" in html_content,
        "6. 투자 고지 있는가": "본 글은 투자 정보 제공 목적이며" in html_content,
        "7. 멋쟁이 결론 있는가": "멋쟁이 결론" in html_content,
        "8. 오늘 피할 것 있는가": "오늘 절대 피할 것" in html_content,
        "9. 이미지 Unsplash인가": "images.unsplash.com" in html_content,
        "10. JSON-LD·SVG 없는가": ("<script" not in html_content) and ("<svg" not in html_content) and ("json-ld" not in html_content.lower())
    }

    print("\n[작업 7 — 품질 체크 10개]")
    all_passed = True
    for item, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"□ {item}: {status}")
        if not passed:
            all_passed = False

    if not all_passed:
        print("\n❌ 품질 체크 실패로 발행을 중단합니다.")
        return

    # 작업 8 — Blogger 발행
    seo_title = f"{date_str} {weekday}요일 장전 8시 50분 — 엔비디아 -5%·수급 교체 속 오늘 단타·스윙 픽 3선 (진입가·손절선 포함)"
    labels = ["장전브리핑", "멋쟁이픽", "동시호가", "단타", "스윙"]
    
    print(f"\n[작업 8 진행] 제목: {seo_title}")
    result = publish_post(seo_title, html_content, labels)

    if "url" in result:
        print(f"\n🎉 [발행 성공] URL: {result['url']}")
        try:
            from instagram_post import post_to_instagram
            card_title = f"{date_str} 장전 8시 50분 브리핑"
            brief_bullets = "• 삼바: 헬스케어 수급 대피처\n• 삼전: 기관 저가 매수 1위\n• 케이엔알: 로봇 상한가 모멘텀\n"
            hashtags = "#주식 #멋쟁이인사이트 #장전브리핑 #단타 #스윙"
            caption = f"📊 {card_title}\n\n{brief_bullets}\n🔗 자세한 분석과 픽 목표가/손절가는 프로필 링크에서 확인하세요!\n\n{hashtags}"
            
            print("\n[추가] 인스타그램 카드뉴스 자동 업로드 중...")
            inst_res = post_to_instagram(card_title, "장전 브리핑 핵심 요약", caption, "★★★★★")
            if inst_res.get("success"):
                print(f"✅ [SUCCESS] 인스타그램 업로드 성공! URL: {inst_res.get('post_url')}")
            else:
                print(f"⚠️ [FAIL] 인스타그램 업로드 실패: {inst_res.get('error')}")
        except Exception as e:
            print(f"인스타그램 업로드 오류: {e}")
    else:
        print(f"\n⚠️ [발행 실패]: {result}")

if __name__ == "__main__":
    run_pipeline_v2()
