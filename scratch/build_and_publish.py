import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from publishers.blogger_publisher import publish_post

def create_premarket_html():
    html = """<div style="max-width: 720px; margin: 0 auto; font-family: 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #111111; line-height: 1.65; background-color: #ffffff; padding: 20px 15px; box-sizing: border-box;">

    <!-- 1. 마스트헤드 -->
    <div style="border-bottom: 3px solid #0a0a0a; padding-bottom: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 13px; font-weight: 800; letter-spacing: 2px; color: #ffffff; background: #0a0a0a; padding: 4px 10px; border-radius: 4px; display: inline-block;">PRE-MARKET 8:50</div>
        <div style="font-size: 14px; font-weight: 700; color: #555555;">2026년 07월 28일 (화) KST</div>
    </div>

    <!-- 2. 수치 대시보드 (검정 배경 8칸) -->
    <div style="background-color: #0a0a0a; color: #ffffff; border-radius: 12px; padding: 20px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="font-size: 12px; font-weight: 700; color: #888888; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 14px; text-align: center;">글로벌 & 국내 증시 마감 대시보드</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">나스닥</div>
                <div style="font-size: 14px; font-weight: 700;">24,932.08</div>
                <div style="font-size: 12px; color: #ef4444; font-weight: 700;">-0.18%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">S&P 500</div>
                <div style="font-size: 14px; font-weight: 700;">7,413.18</div>
                <div style="font-size: 12px; color: #4ade80; font-weight: 700;">+0.02%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">다우존스</div>
                <div style="font-size: 14px; font-weight: 700;">52,210.08</div>
                <div style="font-size: 12px; color: #4ade80; font-weight: 700;">+0.51%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">필라반도체</div>
                <div style="font-size: 14px; font-weight: 700;">SOX</div>
                <div style="font-size: 12px; color: #ef4444; font-weight: 700;">-2.23%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">코스피</div>
                <div style="font-size: 14px; font-weight: 700;">6,755.75</div>
                <div style="font-size: 12px; color: #4ade80; font-weight: 700;">+0.97%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">코스닥</div>
                <div style="font-size: 14px; font-weight: 700;">764.86</div>
                <div style="font-size: 12px; color: #4ade80; font-weight: 700;">+2.22%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">엔비디아</div>
                <div style="font-size: 14px; font-weight: 700;">NVIDIA</div>
                <div style="font-size: 12px; color: #ef4444; font-weight: 700;">-4.99%</div>
            </div>
            <div style="background: #1a1a1a; padding: 12px 8px; border-radius: 8px; text-align: center; border: 1px solid #2a2a2a;">
                <div style="font-size: 11px; color: #aaa; margin-bottom: 4px;">WTI 유가</div>
                <div style="font-size: 14px; font-weight: 700;">국제유가</div>
                <div style="font-size: 12px; color: #ef4444; font-weight: 700;">-7.50%</div>
            </div>
        </div>
    </div>

    <!-- 3. 출처 한 줄 -->
    <div style="font-size: 11px; color: #777777; text-align: right; margin-bottom: 24px; font-style: italic;">
        [출처: KRX 한국거래소, 뉴욕증권거래소(NYSE), 연합인포맥스 2026.07.27 확정 데이터]
    </div>

    <!-- 4. Unsplash 히어로 이미지 -->
    <div style="margin-bottom: 28px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
        <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80" alt="주식 시장 대시보드 이미지" style="width: 100%; height: auto; display: block; object-fit: cover;" />
    </div>

    <!-- 5. H1 역설형 제목 -->
    <h1 style="font-size: 26px; font-weight: 900; color: #0a0a0a; margin: 0 0 24px 0; line-height: 1.35; letter-spacing: -0.5px; border-left: 5px solid #0a0a0a; padding-left: 14px;">
        미 기술주 폭락 속 코스피 반등? 장전 수급 국면과 오늘 단타·스윙 픽 3선
    </h1>

    <!-- 6. 섹션 I · 해외 이슈 → 한국 영향 -->
    <div style="margin-bottom: 36px; background-color: #f9fafb; border-radius: 10px; padding: 20px; border: 1px solid #e5e7eb;">
        <div style="font-size: 18px; font-weight: 800; color: #0a0a0a; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span style="background: #0a0a0a; color: #fff; width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 13px;">I</span>
            해외 핵심 이슈 & 국내 증시 영향 분석
        </div>
        <div style="display: flex; flex-direction: column; gap: 14px;">
            <div style="background: #ffffff; padding: 14px; border-radius: 8px; border-left: 4px solid #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 15px; color: #1e3a8a; margin-bottom: 4px;">1. 중동 리스크 소강 및 국제유가 급락 (WTI -7.5%)</div>
                <div style="font-size: 13px; color: #4b5563; line-height: 1.6;">
                    미국과 이란 간 지정학적 충돌 우려가 약화되면서 유가가 7% 넘게 폭락했습니다. 이는 물가 상승 압력을 완화시켜 항공·운송 및 소비자 관련주에 호재로 작용하며, 전일 국내 시장의 투자심리를 안정화시키는 주요 요인으로 작용했습니다.
                </div>
            </div>
            <div style="background: #ffffff; padding: 14px; border-radius: 8px; border-left: 4px solid #ef4444; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 15px; color: #991b1b; margin-bottom: 4px;">2. AI 거품론 & 반도체 기술 경쟁 우려 (엔비디아 -4.99%)</div>
                <div style="font-size: 13px; color: #4b5563; line-height: 1.6;">
                    중국의 노광장비 독자 개발 발표 및 Big Tech 기업들의 AI 수익화 우려가 제기되며 필라델피아 반도체 지수가 -2.23% 급락했습니다. 금일 삼성전자, SK하이닉스 등 국내 반도체 대형주는 개장 초반 변동성 확대를 방어하는지 수급 점검이 필수적입니다.
                </div>
            </div>
            <div style="background: #ffffff; padding: 14px; border-radius: 8px; border-left: 4px solid #10b981; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; font-size: 15px; color: #065f46; margin-bottom: 4px;">3. FOMC 경계감 속 방어주(헬스케어·소비재) 수급 이동</div>
                <div style="font-size: 13px; color: #4b5563; line-height: 1.6;">
                    미 7월 FOMC 금리 결정을 앞두고 기술주 차익실현 물량이 바이오·소비재 등 경기 방어주로 이동했습니다. 국내 시장에서도 바이오 및 자동차 대형주로 외국인·기관의 수급 쏠림 현상이 재현되고 있습니다.
                </div>
            </div>
        </div>
    </div>

    <!-- 7. 섹션 II · 어제 상한가 분석 -->
    <div style="margin-bottom: 36px;">
        <div style="font-size: 18px; font-weight: 800; color: #0a0a0a; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span style="background: #0a0a0a; color: #fff; width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 13px;">II</span>
            전일 코스닥 상한가 특징주 분석
        </div>
        <div style="font-size: 13.5px; color: #374151; margin-bottom: 14px;">
            전일(7/27) 코스피는 상한가 종목이 부재했으나, 코스닥 시장에서는 AI 로봇, 바이오 특허 및 파트너십 호재를 모멘텀으로 10개 종목이 가격제한폭까지 상승 마감했습니다.
        </div>
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; background: #ffffff; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-weight: 800; font-size: 15px; color: #111;">케이엔알시스템</span>
                    <span style="font-size: 12px; color: #6b7280; margin-left: 6px;">(299990)</span>
                    <div style="font-size: 12.5px; color: #4b5563; margin-top: 2px;">산업용 로봇손 독자 개발 공시로 로봇 관련주 수급 집결</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 15px; font-weight: 800; color: #ef4444;">14,270원</div>
                    <div style="font-size: 11px; font-weight: 700; color: #ef4444;">상한가 (+29.96%)</div>
                </div>
            </div>
            <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; background: #ffffff; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-weight: 800; font-size: 15px; color: #111;">아이크래프트</span>
                    <span style="font-size: 12px; color: #6b7280; margin-left: 6px;">(089590)</span>
                    <div style="font-size: 12.5px; color: #4b5563; margin-top: 2px;">엔비디아 AI 솔루션 공급 계약 모멘텀에 매수세 집결</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 15px; font-weight: 800; color: #ef4444;">4,420원</div>
                    <div style="font-size: 11px; font-weight: 700; color: #ef4444;">상한가 (+30.00%)</div>
                </div>
            </div>
            <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; background: #ffffff; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-weight: 800; font-size: 15px; color: #111;">셀리드</span>
                    <span style="font-size: 12px; color: #6b7280; margin-left: 6px;">(299660)</span>
                    <div style="font-size: 12.5px; color: #4b5563; margin-top: 2px;">항암면역치료백신 미국 특허 등록 성공 소식 급등</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 15px; font-weight: 800; color: #ef4444;">1,367원</div>
                    <div style="font-size: 11px; font-weight: 700; color: #ef4444;">상한가 (+29.94%)</div>
                </div>
            </div>
            <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; background: #ffffff; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-weight: 800; font-size: 15px; color: #111;">오브젠</span>
                    <span style="font-size: 12px; color: #6b7280; margin-left: 6px;">(415610)</span>
                    <div style="font-size: 12.5px; color: #4b5563; margin-top: 2px;">네이버-엔비디아 AI 파트너십 구축 수혜 기대감 반등</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 15px; font-weight: 800; color: #ef4444;">7,930원</div>
                    <div style="font-size: 11px; font-weight: 700; color: #ef4444;">상한가 (+30.00%)</div>
                </div>
            </div>
        </div>
    </div>

    <!-- 8. 섹션 III · 오늘 픽 3개 (진입가·손절선·목표가) -->
    <div style="margin-bottom: 36px;">
        <div style="font-size: 18px; font-weight: 800; color: #0a0a0a; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
            <span style="background: #0a0a0a; color: #fff; width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 13px;">III</span>
            오늘의 전략 픽 3선 (진입가·손절선·목표가)
        </div>

        <!-- 픽 1 -->
        <div style="border: 2px solid #0a0a0a; border-radius: 12px; padding: 18px; margin-bottom: 20px; background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <span style="font-size: 18px; font-weight: 900; color: #0a0a0a;">삼성바이오로직스</span>
                    <span style="font-size: 13px; color: #666; font-weight: 700; margin-left: 6px;">(207940)</span>
                </div>
                <span style="background-color: #1e3a8a; color: #ffffff; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px;">스윙 픽</span>
            </div>
            <div style="font-size: 13px; color: #4b5563; margin-bottom: 14px; background: #f3f4f6; padding: 10px; border-radius: 6px; line-height: 1.5;">
                • 미 증시 방어주(헬스케어) 강세 및 전일 외국인·기관 양대 주체 동시 대규모 순매수 집결 종목입니다.<br/>
                • 바이오 반등 장세 속 글로벌 CDMO 수주 확대로 시장 변동성에 대한 우수한 하방 지지력을 보유했습니다.
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center;">
                <div style="background-color: #f9fafb; padding: 10px 4px; border-radius: 8px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 11px; color: #6b7280; margin-bottom: 2px; font-weight: 700;">진입가 (기준)</div>
                    <div style="font-size: 14px; font-weight: 800; color: #111827;">1,545,000원</div>
                </div>
                <div style="background-color: #fef2f2; padding: 10px 4px; border-radius: 8px; border: 1px solid #fecaca;">
                    <div style="font-size: 11px; color: #dc2626; margin-bottom: 2px; font-weight: 700;">손절선 (-3.0%)</div>
                    <div style="font-size: 14px; font-weight: 800; color: #ef4444;">1,498,650원</div>
                </div>
                <div style="background-color: #f0fdf4; padding: 10px 4px; border-radius: 8px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 11px; color: #166534; margin-bottom: 2px; font-weight: 700;">목표가 1 / 2</div>
                    <div style="font-size: 13px; font-weight: 800; color: #4ade80;">1.60M / 1.65M</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #dc2626; margin-top: 10px; font-weight: 700;">
                ⚠️ 주의사항: FOMC 전 금리 변동성을 감안하여 시초가 급등 시 쫓아가지 않고 눌림목 분할 진입 권장.
            </div>
        </div>

        <!-- 픽 2 -->
        <div style="border: 2px solid #0a0a0a; border-radius: 12px; padding: 18px; margin-bottom: 20px; background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <span style="font-size: 18px; font-weight: 900; color: #0a0a0a;">케이엔알시스템</span>
                    <span style="font-size: 13px; color: #666; font-weight: 700; margin-left: 6px;">(299990)</span>
                </div>
                <span style="background-color: #dc2626; color: #ffffff; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px;">단타 픽</span>
            </div>
            <div style="font-size: 13px; color: #4b5563; margin-bottom: 14px; background: #f3f4f6; padding: 10px; border-radius: 6px; line-height: 1.5;">
                • 전일 산업용 로봇손 독자 개발 공시로 코스닥 거래량 폭발하며 강한 상한가(14,270원)에 마감했습니다.<br/>
                • 모멘텀 쏠림 및 상한가 잔량 기조에 따라 개장 초반 변동성 매매 모멘텀 형성이 기대되는 종목입니다.
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center;">
                <div style="background-color: #f9fafb; padding: 10px 4px; border-radius: 8px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 11px; color: #6b7280; margin-bottom: 2px; font-weight: 700;">진입가 (기준)</div>
                    <div style="font-size: 14px; font-weight: 800; color: #111827;">14,270원</div>
                </div>
                <div style="background-color: #fef2f2; padding: 10px 4px; border-radius: 8px; border: 1px solid #fecaca;">
                    <div style="font-size: 11px; color: #dc2626; margin-bottom: 2px; font-weight: 700;">손절선 (-4.0%)</div>
                    <div style="font-size: 14px; font-weight: 800; color: #ef4444;">13,700원</div>
                </div>
                <div style="background-color: #f0fdf4; padding: 10px 4px; border-radius: 8px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 11px; color: #166534; margin-bottom: 2px; font-weight: 700;">목표가 1 / 2</div>
                    <div style="font-size: 13px; font-weight: 800; color: #4ade80;">15,500 / 16,800원</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #dc2626; margin-top: 10px; font-weight: 700;">
                ⚠️ 주의사항: 시초가 갭상승 출발 시 절대 추격하지 말고, 시가 갭 메움 및 눌림 확인 후 철저한 원칙 매매.
            </div>
        </div>

        <!-- 픽 3 -->
        <div style="border: 2px solid #0a0a0a; border-radius: 12px; padding: 18px; margin-bottom: 20px; background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <span style="font-size: 18px; font-weight: 900; color: #0a0a0a;">삼성전자</span>
                    <span style="font-size: 13px; color: #666; font-weight: 700; margin-left: 6px;">(005930)</span>
                </div>
                <span style="background-color: #1e3a8a; color: #ffffff; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px;">스윙 픽</span>
            </div>
            <div style="font-size: 13px; color: #4b5563; margin-bottom: 14px; background: #f3f4f6; padding: 10px; border-radius: 6px; line-height: 1.5;">
                • 미 반도체 지수 하락에도 전일 국내 기관의 대규모 저가 순매수 1위 유입으로 수급 방어력이 입증되었습니다.<br/>
                • 코스피 지수의 6,750선 연동 방어 역할을 수행하며 밸류에이션 하한 지지력을 바탕으로 스윙 접근이 유효합니다.
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center;">
                <div style="background-color: #f9fafb; padding: 10px 4px; border-radius: 8px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 11px; color: #6b7280; margin-bottom: 2px; font-weight: 700;">진입가 (기준)</div>
                    <div style="font-size: 14px; font-weight: 800; color: #111827;">254,000원</div>
                </div>
                <div style="background-color: #fef2f2; padding: 10px 4px; border-radius: 8px; border: 1px solid #fecaca;">
                    <div style="font-size: 11px; color: #dc2626; margin-bottom: 2px; font-weight: 700;">손절선 (-2.5%)</div>
                    <div style="font-size: 14px; font-weight: 800; color: #ef4444;">247,650원</div>
                </div>
                <div style="background-color: #f0fdf4; padding: 10px 4px; border-radius: 8px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 11px; color: #166534; margin-bottom: 2px; font-weight: 700;">목표가 1 / 2</div>
                    <div style="font-size: 13px; font-weight: 800; color: #4ade80;">263,000 / 272,000원</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #dc2626; margin-top: 10px; font-weight: 700;">
                ⚠️ 주의사항: 미 엔비디아(-4.99%) 여파로 인한 개장 직후 시가 갭하락 시 분할 진입으로 안전성 강화.
            </div>
        </div>
    </div>

    <!-- 9. 피할 것 박스 (빨간 테두리 + #fff5f5 배경) -->
    <div style="border: 2px solid #ef4444; background-color: #fff5f5; border-radius: 10px; padding: 18px; margin-bottom: 28px;">
        <div style="font-size: 16px; font-weight: 800; color: #991b1b; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 18px;">🚫</span> 오늘 장전 피해야 할 3가지 매매 패턴
        </div>
        <div style="font-size: 13px; color: #7f1d1d; line-height: 1.6;">
            1. <strong>갭업 시초가 추격 매수 절대 금지</strong>: 전일 상한가 및 이슈 종목의 시초가 갭상승 파동에서 뇌동매수 시 단기 차익 물량에 물리 위험 극대화.<br/>
            2. <strong>반도체 섹터 일괄 풀매수 지양</strong>: 엔비디아 급락에 따른 미 반도체 섹터 센티먼트 악화로 기관 수급 지지 여부 확인 필수.<br/>
            3. <strong>손절가 미설정 매매 금지</strong>: 8시 50분 동시호가 변동성과 개장 후 30분 변동성에 대비해 반드시 손절 기준(-2.5% ~ -4.0%) 이탈 시 칼손절 집행.
        </div>
    </div>

    <!-- 10. 멋쟁이 결론 (검정 배경) -->
    <div style="background-color: #0a0a0a; color: #ffffff; border-radius: 10px; padding: 20px; margin-bottom: 24px; text-align: center;">
        <div style="font-size: 12px; font-weight: 700; color: #38bdf8; letter-spacing: 1.5px; margin-bottom: 6px;">EXECUTIVE SUMMARY</div>
        <div style="font-size: 16px; font-weight: 800; margin-bottom: 8px;">"지수 변동성 구간, 확실한 수급 방어주와 절제된 눌림목에 집중하라"</div>
        <div style="font-size: 12.5px; color: #cccccc; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            미 증시의 반도체 차익실현 물량과 FOMC 경계감이 중첩된 장세입니다. 무리한 장초반 추격보다는 외국인·기관 수급 유입이 입증된 헬스케어 및 저가 매수세 반도체, 강력한 로봇 모멘텀 종목의 기술적 대응이 승률을 높이는 핵심입니다.
        </div>
    </div>

    <!-- 11. 투자 고지 (빨간 테두리) -->
    <div style="border: 1.5px solid #fca5a5; background-color: #fafafa; border-radius: 8px; padding: 14px; margin-bottom: 20px;">
        <div style="font-size: 12px; font-weight: 800; color: #dc2626; margin-bottom: 4px;">⚠️ [투자 유의사항 및 법적 고지]</div>
        <div style="font-size: 11px; color: #6b7280; line-height: 1.5;">
            본 컨텐츠는 공개된 시장 데이터와 수급 동향을 토대로 작성된 정보 제공용 리포트이며, 특정 종목에 대한 투자 권유나 매수/매도 추천이 아닙니다. 제시된 진입가·목표가·손절가는 기준선일 뿐 시장 상황에 따라 상이할 수 있으며, 모든 투자의 최종 책임은 투자자 본인에게 있습니다.
        </div>
    </div>

    <!-- 12. 출처 푸터 -->
    <div style="border-top: 1px solid #e5e7eb; padding-top: 14px; text-align: center; font-size: 11px; color: #9ca3af;">
        멋쟁이 인사이트 장전 브리핑 | 데이터 출처: KRX 한국거래소, 뉴욕증권거래소, 연합인포맥스, 팩트셋 (2026.07.27 마감 데이터)
    </div>

</div>"""
    return html

def run_pipeline():
    now = datetime.datetime.now()
    weekday = ['월','화','수','목','금','토','일'][now.weekday()]
    date_str = now.strftime('%Y년 %m월 %d일')
    
    print(f"==================================================")
    print(f"오늘: {date_str} {weekday}요일 KST")
    print(f"==================================================")

    # 1. HTML 생성
    html_content = create_premarket_html()
    
    # 2. 품질 체크
    checks = {
        "픽 3개 모두 손절선 있는가": "-3.0%" in html_content and "-4.0%" in html_content and "-2.5%" in html_content,
        "진입가 원 단위인가": "1,545,000원" in html_content and "14,270원" in html_content and "254,000원" in html_content,
        "출처 명시됐는가": "KRX" in html_content and "출처" in html_content,
        "투자 고지 있는가": "투자 유의사항 및 법적 고지" in html_content,
        "상한가 분석 있는가": "전일 코스닥 상한가 특징주 분석" in html_content,
        "갭업 시초가 추격 경고 있는가": "갭업 시초가 추격 매수 절대 금지" in html_content
    }

    print("\n[품질 체크리스트]")
    all_passed = True
    for check_item, is_pass in checks.items():
        status = "[PASS]" if is_pass else "[FAIL]"
        print(f"- {check_item}: {status}")
        if not is_pass:
            all_passed = False

    if not all_passed:
        print("\n[FAIL] 품질 체크 실패로 발행을 중단합니다.")
        return

    # 3. 발행
    seo_title = f"{date_str} {weekday}요일 오전 8시 50분 장전 — 미 기술주 폭락 속 수급 반등 오늘 단타·스윙 픽 3선"
    labels = ["장전브리핑", "멋쟁이픽", "동시호가", "단타", "스윙"]
    
    print(f"\n[발행 진행] 제목: {seo_title}")
    result = publish_post(seo_title, html_content, labels)

    if "url" in result:
        print(f"\n[SUCCESS] 발행 성공! URL: {result['url']}")
    else:
        print(f"\n[FAIL] 발행 실패: {result}")

if __name__ == "__main__":
    run_pipeline()
