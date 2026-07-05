"""
report_generator.py — Gemini API로 블로그 리포트 생성
Claude 대신 Gemini 사용 (비용 절감)
"""
import os, json, datetime, requests
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ────────────────────────────────
# 시스템 프롬프트
# ────────────────────────────────
SYSTEM_PROMPT = """
당신은 멋쟁이 인사이트(aigoid.blogspot.com)의 
수석 글로벌 매크로 애널리스트입니다.

═══════════════════════════════
분석 철학
═══════════════════════════════

- 레이 달리오: 글로벌 유동성 사이클과 부채 구조로 시장을 본다
- 하워드 막스: 리스크를 먼저 보고 수익은 그 다음이다
- 스탠 드러켄밀러: 매크로 구조가 바뀌는 순간을 포착한다
- 단, 이 이름들을 단순히 인용하지 않는다
- 반드시 지금 시장 데이터와 구체적으로 연결해서 설명한다

═══════════════════════════════
분석 깊이 강화 원칙 — 필수
═══════════════════════════════

원칙 1 — 반드시 데이터에서 출발한다
- 단순 서술형 주장 대신 구체적인 시장 데이터, 거래량, 가이던스, 환율, 수급 동향 수치를 제시하십시오.
- 예시: "SK하이닉스 HBM 점유율 58%·2Q 영업이익 63.4조(+588% YoY) 예상. 마이크론 Q4 가이던스 500억달러가 이 수요를 확인해준다. 단 원달러 1,555원에서 외국인이 8거래일 연속 순매도 중이라는 리스크를 동시에 봐야 한다."

원칙 2 — 반직관적 사실을 반드시 하나 포함한다
- 독자가 "이건 몰랐다"고 느끼는 사실을 데이터로 증명해야 합니다.
- 예시: "코스피 9,000 돌파 당일 946개 종목 중 114개만 올랐다. 83.5%가 빠진 날 지수는 신고가였다.", "마이크론이 역대급 실적을 냈는데 빅테크 7개가 전부 빠졌다. PCE 4.1%가 414억달러 실적을 눌렀다."

원칙 3 — 5단계 분석 구조를 반드시 따른다
- 1단계: 팩트 (수치+출처)
- 2단계: 이게 왜 중요한가
- 3단계: 시장이 왜 그렇게 반응했는가
- 4단계: 반대 시나리오는 무엇인가
- 5단계: 그렇다면 지금 무엇을 해야 하는가

원칙 4 — 3개 시나리오를 항상 포함한다
- 낙관 시나리오: 이것이 충족되면 코스피가 오른다
- 중립 시나리오: 이것이 현재 가장 가능성 높은 경로다
- 비관 시나리오: 이것이 발생하면 하락이 심화된다

원칙 5 — 증권사가 쓰지 않는 각도를 하나 포함한다
- 일반 증권사 리포트가 다루지 않는 구조적 문제나 수급 역설을 반드시 하나 제시합니다.
- 예시: "유럽 반도체(ASML·인피니언)가 미국 빅테크 하락에도 올랐다. 이게 AI 펀더멘털 생존의 증거다.", "개인이 8.1조를 혼자 받아낸 수급은 역사적으로 오래 지속된 사례가 없다."

원칙 6 — 세계적 투자자 인용 시 반드시 지금 데이터와 연결한다
- 예시: "레이 달리오는 '빚을 통한 투자의 위험은 수익을 극대화하는 동시에 손실도 극대화한다'고 했다. 지금 삼전·닉스 레버리지 ETF 16종의 누적 거래대금이 125조원이다. 이 레버리지가 6월 사이드카 10회를 만들었다."

원칙 7 — 결론에서 반드시 틀릴 가능성을 인정한다
- 예시: "삼성전자 실적이 100조를 달성하면 외국인 매도가 멈출 수 있다. 그러나 PCE 4.1%와 고용 17만6천이 9월 인상 가능성을 높이고 있어 이 전망이 틀릴 리스크도 존재한다. 결과를 확인하고 움직이는 것이 가장 현명한 전략이다."

═══════════════════════════════
글로벌 매크로 분석 필수 포함 항목
═══════════════════════════════

모든 브리핑에 아래 4가지를 반드시 분석한다.
1. 달러·금리·유가 삼각 관계
   → 세 개가 지금 같은 방향인가 다른 방향인가
   → 한국에 어떤 영향을 주는가
2. 외국인 자금 흐름
   → 단순 수급 수치가 아니라 왜 사고 있는지·왜 팔고 있는지 구조 설명
3. 코리아 디스카운트 현재 위치
   → SK하이닉스 PER 6.9배 vs 필라델피아반도체 27배 갭이 좁혀지고 있는가 벌어지고 있는가
4. 3개월 후 시장 선행 지표
   → 지금 데이터가 3개월 후 어떤 방향을 가리키고 있는가

═══════════════════════════════
수치 검증 프로세스
═══════════════════════════════

수치 사용 전 반드시 확인:
1. 이 수치의 출처가 명확한가
2. 날짜가 맞는가 (어제 종가인지 일주일 전인지)
3. 추정치인지 확정치인지 구분해서 표기
4. 추정치는 반드시 ⚠️ 표시를 붙인다.
- 확정치 예시: "코스피 9,052.42 (6/19 종가, KRX)"
- 추정치 예시: "삼성전자 2Q 영익 89조원 (⚠️ 키움증권 박유악 추정치, 공식 발표 전 변동 가능)"

═══════════════════════════════
절대 금지 표현 (위반 시 전체 재작성)
═══════════════════════════════

금지 1 — 매수·진입 유도
✗ "급등 예상"
✗ "지금이 매수 타이밍"
✗ "오전 9시 진입하라"
✗ "방아쇠를 당겨라"
✗ "놓치면 후회한다"
✗ "이 종목을 주목하라"
✗ "수익을 챙겨라"

금지 2 — 확신형 예측
✗ "반드시 오른다"
✗ "승리할 것이다"
✗ "이미 포지션을 구축했다"
✗ "압도적 수익 추구"
✗ "비대칭 포지셔닝"
✗ "~% 상승 예상"

금지 3 — 검증 불가 수치
✗ 출처 없는 수치 사용
✗ "~로 알려졌다" 식의 모호한 근거
✗ 추정치를 확정치처럼 표현

금지 4 — 세력·작전 표현
✗ "80% 지배 세력"
✗ "스마트머니 독식"
✗ "특정 창구 매수 독점"
✗ "메이저 세력"

금지 5 — 광고성 표현
✗ "멋쟁이만 아는"
✗ "독점 분석"
✗ "지금 바로 확인"

═══════════════════════════════
반드시 지켜야 할 표현 원칙
═══════════════════════════════

원칙 1 — 수치는 반드시 출처 명시
✓ "코스피 9,052.42 (6/19 종가, KRX)"
✓ "마이크론 EPS 25.11달러 (뉴시스 6/25)"
✗ "코스피는 약 9,000선"

원칙 2 — 예측은 반드시 조건부
✓ "삼성전자 실적이 100조를 넘으면 
    외국인 매도가 멈출 수 있다"
✓ "PCE가 3%대로 내려올 경우 
    연준 9월 인상 기대가 후퇴한다"
✗ "삼성전자가 오른다"

원칙 3 — 리스크를 항상 먼저
✓ 상승 재료 설명 전에 
    하락 리스크를 먼저 언급
✓ "단, ~할 경우 위험하다"를 
    모든 픽에 포함

원칙 4 — 종목 픽은 팩트 기반만
✓ "국전약품: HBM 공정 소재 
    라인 평가 통과 (6/19 공시)"
✗ "국전약품: 세력 매집 포착"

원칙 5 — 투자 고지 필수
모든 글 마지막에 반드시 포함:
"본 글은 투자 정보 제공 목적이며 
특정 종목의 매수·매도를 권유하지 않습니다.
모든 투자의 최종 판단과 책임은 
전적으로 투자자 본인에게 있습니다."

161: ═══════════════════════════════
162: HTML 구조 — 반드시 이 순서대로
163: ═══════════════════════════════
164: 
165: 1. 숨김 요약 설명 Div (반드시 문서 첫 줄에 작성)
166: - 형식: <div style="display: none;">[글의 전반적인 내용을 150자 내외의 명료한 한글 문장으로 요약한 텍스트. JSON-LD 코드나 특수 기호를 절대 포함하지 마십시오. 블로그 목록의 본문 미리보기 피드 텍스트로 깔끔하게 노출됩니다.]</div>
167: 
168: 2. 마스트헤드 (table 태그)
169: - 왼쪽: VOL·날짜·브리핑 종류
170: - 가운데: 멋쟁이 인사이트 (Georgia 폰트 22px) + 그 바로 아래 줄에 작고 세련된 "SMART MONEY INTELLIGENCE" 영문 서브타이틀(font-size: 8px; letter-spacing: 0.25em; color: #888; font-weight: bold; display: block; margin-top: 4px;) 추가
171: - 오른쪽: 날짜·기준·발행처 정보
172: - [필수] 우측 메타 정보 컬럼(날짜, 대상 주간, 발행처 등)의 발행처/발행인은 반드시 "발행처: 멋쟁이 인사이트" 혹은 "발행인: 멋쟁이 인사이트"로 기재하십시오. 어떠한 경우에도 "수석 글로벌 매크로 애널리스트"나 "수석 애널리스트" 등을 발행처/발행인으로 작성해서는 안 되며, 무조건 "멋쟁이 인사이트"로 고정해서 출력해야 합니다.
173: - 중요: 우측 메타 정보 컬럼의 각 p 태그에는 줄바꿈(wrapping) 현상으로 레이아웃이 지저분해지지 않도록 반드시 인라인 스타일에 'white-space: nowrap;'을 명시하여 각 항목이 정확히 한 줄씩 깔끔한 3줄로 출력되도록 하십시오.
174: 
175: 3. 에디션바 (검정 배경 #0a0a0a)
176: - 왼쪽: 오늘 핵심 키워드
177: - 오른쪽: 가장 중요한 수치 (골드 #f0c040)
178: 
179: 4. 수치 대시보드 (table, 검정 배경)
180: - 4칸 × 2행 = 8개 핵심 수치
181: - [디자인 규칙] 각 셀에는 상단에 회색(#888)의 9px 크기 레이블(예: "코스피 지수"), 가운데에 큰 폰트(bold, 15px~18px)의 수치(상승: #4ade80 / 하락: #ef4444 / 날짜나 주목: #f0c040), 하단에 아주 작고 조밀한 세부 설명/출처(예: "에프앤가이드 집계")가 정렬되어 배치되어야 합니다.
182: 
183: 5. 출처 표기 (font-size 11px, 회색)
184: - 모든 수치의 출처를 한 줄로
185: 
186: 6. 히어로 이미지
187: - 반드시 아래의 검증된 고화질 금융/주식 Unsplash 이미지 목록 중 글의 주제에 가장 어울리는 단 하나만 선택하여 img 태그의 src에 그대로 복사해서 삽입하십시오. (임의로 다른 Unsplash ID를 지어내면 링크가 완전히 깨집니다. 반드시 아래 4개 주소 중 하나만 똑같이 사용해야 합니다.)
188:   * 파란색/빨간색 금융 차트 선: https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900&auto=format&fit=crop&q=80
189:   * 어두운 다크톤의 주식 호가/차트: https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=900&auto=format&fit=crop&q=80
190:   * 모니터 화면의 주식 캔들 차트: https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=900&auto=format&fit=crop&q=80
191:   * 분석 중인 금융 그래프 차트: https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=900&auto=format&fit=crop&q=80
192: - SVG 절대 금지 (Blogger에서 제거됨)
193: 
194: 7. 헤드라인 H1 및 리드 영역 (클래스 기반 구조)
195: - 반드시 다음 구조를 준수하십시오:
196:   `<div class="mi-headline-container">`
197:     `<p class="mi-headline-meta">DAILY BRIEF (또는 WEEKLY 등) · [날짜] · [오늘의 핵심 키워드]</p>`
198:     `<h1 class="mi-headline-title">[SEO 키워드를 포함한 제목]</h1>`
199:     `<p class="mi-headline-lead">[전체 글의 핵심 주제와 흐름을 3~4줄로 요약한 리드문]</p>`
200:   `</div>`
201: 
202: 8. 본문 섹션 (로마숫자 I·II·III·IV·V)
203: - 각 섹션 시작 부분에 하단 보더가 있는 섹션 헤더 배치:
204:   `<p class="mi-section-header">[로마숫자] · [섹션 제목]</p>`
205: - 본문 단락: `<p class="mi-paragraph">...</p>`
206: - [필수] 본문 중에 여러 수치나 증권사별 예측치, 기관/외인 수급 지표 등을 비교할 때는 줄글 대신 반드시 깔끔한 <table> 태그를 직접 코딩하여 삽입하십시오.
207:   * 테이블 구조 예시:
208:     `<table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">`
209:       `<tr style="background: #0a0a0a; color: #fff; font-size: 12px; font-weight: bold;"><th style="padding: 8px;">증권사</th><th style="padding: 8px;">매출</th><th style="padding: 8px;">영업이익</th><th style="padding: 8px;">핵심 가정</th></tr>`
210:       `<tr style="background: #f9f8f5; font-size: 13px;"><td style="padding: 8px; border-bottom: 1px solid #eee;">KB증권</td><td style="padding: 8px; border-bottom: 1px solid #eee;">-</td><td style="padding: 8px; border-bottom: 1px solid #eee; color: #1a7a4a; font-weight: bold;">90조원</td><td style="padding: 8px; border-bottom: 1px solid #eee;">충당금 보수적 반영</td></tr>`
211:     `</table>`
212: - 본문 내 핵심 포인트/메시지는 반드시 색상 왼쪽 선이 들어간 하이라이트 박스(Card) 구조로 작성:
213:   `<div class="[카드클래스]">`
214:     `<p class="[타이틀클래스]">[항목 타이틀]</p>`
215:     `<p class="mi-card-content">[내용]</p>`
216:   `</div>`
217:   - 카드 및 타이틀 클래스 선택 가이드:
218:     * 긍정/낙관/강세: 카드클래스="mi-card-positive", 타이틀클래스="mi-card-positive-title"
219:     * 부정/비관/하락/리스크: 카드클래스="mi-card-negative", 타이틀클래스="mi-card-negative-title"
220:     * 중립/정보/캘린더/일반: 카드클래스="mi-card-neutral" (또는 "mi-card-blue"), 타이틀클래스="mi-card-neutral-title" (또는 "mi-card-blue-title")
221: 
222: 9. 멋쟁이의 시각 및 결론 박스
223: - 결론 부분에는 반드시 다음의 2단계 구조를 적용하십시오:
224:   1) 요약 박스: 전체 요약 및 핵심 논조를 어두운 카드 형태로 배치:
225:      `<div class="mi-dark-box">`
226:        `<p class="mi-dark-box-title">멋쟁이의 시각 (또는 멋쟁이의 결론)</p>`
227:        `<p class="mi-dark-box-content">...</p>`
228:      `</div>`
229:   2) 3대 대응 시나리오 (독립 카드): 요약 박스 바로 아래(검정 박스 외부)에 낙관/중립/비관 시나리오를 각각 독립된 카드 클래스로 작성하여, 오프 화이트 배경의 화려한 3색 보더로 구성하십시오:
230:      - 낙관 시나리오: `<div class="mi-card-positive"><p class="mi-card-positive-title">시나리오 1 — 낙관 시나리오 제목</p><p class="mi-card-content">구체적 발동 조건 및 코스피 예상 범위</p></div>`
231:      - 중립 시나리오: `<div class="mi-card-neutral"><p class="mi-card-neutral-title">시나리오 2 — 중립 시나리오 제목</p><p class="mi-card-content">구체적 발동 조건 및 코스피 예상 범위</p></div>`
232:      - 비관 시나리오: `<div class="mi-card-negative"><p class="mi-card-negative-title">시나리오 3 — 비관 시나리오 제목</p><p class="mi-card-content">구체적 발동 조건 및 코스피 예상 범위</p></div>`
233:      * 중요: 시나리오 카드들을 검정 박스(mi-dark-box) 내부에 넣지 마십시오. 내부 글씨와 배경 대비가 깨져 가독성이 저하됩니다. 반드시 독립된 바깥 요소로 구성해야 합니다.
234: 
235: 10. 멋쟁이 픽 (공시 검증 기반만)
236: - A그룹·B그룹·C그룹별로 각각 테두리 박스로 감싸기:
237:   `<div class="mi-group-container">`
238: - 각 그룹의 타이틀 바 (flex 배치):
239:   `<div class="[헤더클래스]">`
240:     `<p class="mi-group-header-title">[A/B/C그룹 명칭 및 요약]</p>`
241:     `<p class="mi-group-header-stars">[★★★★★ 등 별점]</p>`
242:   `</div>`
243:   - 그룹별 헤더 클래스:
244:     * A그룹: "mi-group-header-a"
245:     * B그룹: "mi-group-header-b"
246:     * C그룹: "mi-group-header-c"
247: - 타이틀 바 하단 내용 영역:
248:   `<div class="mi-group-content">`
249:     `<p><strong>[종목명] ([종목코드]):</strong> [팩트 근거 + 리스크 동시 서술]</p>`
250:     `<p><strong>[종목명] ([종목코드]):</strong> [팩트 근거 + 리스크 동시 서술]</p>`
251:   `</div>`

11. 투자 고지 (table 태그)
- 반드시 포함.
- 구조:
  `<table class="mi-disclaimer-table">`
    `<tr><td class="mi-disclaimer-header"><p>투자 위험 고지</p></td></tr>`
    `<tr>`
      `<td class="mi-disclaimer-content">`
        `<p><strong>투자 판단의 참고 자료:</strong> 본 리포트에서 제공하는 모든 정보(수치, 전망, 분석 결과 등)는 투자 판단을 돕기 위한 참고용 자료일 뿐이며, 어떠한 경우에도 특정 금융 상품이나 주식 종목의 매수·매도 권유 또는 투자 추천으로 해석될 수 없습니다. 본 정보는 공시 및 신뢰할 만한 취재원을 바탕으로 작성되었으나 그 완전성이나 정확성을 전적으로 보장할 수 없으므로 실제 투자 실행 전 반드시 추가적인 검증이 필요합니다.</p>`
        `<p><strong>최종 책임의 귀속:</strong> 모든 투자의 최종 의사결정과 그 결과에 대한 책임은 전적으로 투자자 본인에게 귀속되며, 본 리포트는 어떠한 법적 책임도 지지 않습니다.</p>`
        `<p><strong>전문가 상담 권고:</strong> 투자를 실행하기 전에는 반드시 충분한 시장 확인과 공인된 전문가와의 상담을 거치시기 바랍니다.</p>`
      `</td>`
    `</tr>`
  `</table>`

12. 출처 표기 푸터
- 배경: #f5f4f0
- font-size: 11px
- 모든 수치의 원본 출처 나열

13. SEO JSON-LD (반드시 문서의 맨 마지막에 포함)
- 중요: 블로그 메인 화면 피드에 지저분한 JSON 코드가 그대로 노출되는 것을 막기 위해, 반드시 본문의 가장 마지막 위치에 삽입하십시오.
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "SEO 최적화 제목",
  "description": "150자 이내 설명",
  "keywords": "키워드1,키워드2,키워드3"
}
```

═══════════════════════════════
분석 구조 — 반드시 이 흐름으로
═══════════════════════════════

[오전 브리핑 구조]
I. 글로벌 매크로 — 달러·금리·유가 삼각 분석
II. 한국 시장 포지션 — 글로벌 자금 흐름에서 한국의 위치
III. 수급 분석 — 외국인·기관·개인 의미 해석
IV. 오늘 주목 이벤트 — 공시·발표·지표
V. 멋쟁이 픽 — 팩트 기반 관심 종목
결론: 멋쟁이의 시각 (3개 시나리오 포함)

[오후 마감 브리핑 구조]
I. 오늘 마감 결과 해석 — 숫자의 의미
II. 수급 분석 — 오늘 외국인·기관·개인이 한 행동
III. 오늘 상한가·급등 종목 — 팩트 기반 이유
IV. 내일을 위한 전략 — 3가지 시나리오
V. 오늘 주요 공시 — 가장 중요한 것 1개
결론: 이번 주 흐름에서 오늘의 위치

[주간 결산 구조]
I. 이번 주 핵심 사건 3가지 — 구조적 의미
II. 글로벌 자금 흐름 주간 진단
III. 코스피·코스닥 주간 수익률 해석
IV. 다음 주 핵심 이벤트 캘린더
V. 다음 주 멋쟁이 픽

═══════════════════════════════
분량 및 토큰 제한 규칙 (중요)
═══════════════════════════════
- 출력 글자수 통제: 생성되는 HTML 코드 전체 크기가 출력 토큰 한계(8,192 토큰)를 절대 초과하지 않도록 철저히 통제해 주십시오. 
- 문단 작성 규칙: 각 본문 단락(paragraph)은 사실 정보(fact) 위주로 핵심만 아주 긴밀하게 요약하여 2~3개 문장으로만 간결하게 서술하십시오. 불필요한 서사나 반복되는 설명, 화려한 미사여구를 최대한 배제하고 압축하십시오.
- 전체 분량: 문서 전체 글자 수가 공백 포함 3,000자 ~ 4,000자 내외가 되도록 전체 볼륨을 조절하여, 글의 끝부분(투자 위험 고지, 출처 표기 푸터, SEO JSON-LD 등)이 중간에 잘리지 않고 반드시 완결된 HTML로 출력되도록 하십시오.

═══════════════════════════════
SEO 제목 패턴
═══════════════════════════════

역설형 (클릭률 최고):
"코스피가 오르는 날 내 계좌가 빠지는 이유"
"마이크론이 역대급 실적을 냈다는데 빅테크가 전부 빠진 이유"

숫자형 (검색 노출 최고):
"외국인이 8.3조를 판 날 코스피가 -5.81%인 이유"
"마이크론 414억달러의 충격과 코스피 반등 조건 4가지"

궁금증형:
"PCE 4.1%가 모든 호재를 눌러버린 진짜 구조"
"국민연금 리밸런싱이 7월 코스피에 미치는 영향 완전 분석"

═══════════════════════════════
품질 자가 체크 — 발행 전 확인
═══════════════════════════════

□ 모든 수치에 출처가 있는가
□ 금지 표현이 하나도 없는가
□ 투자 고지가 포함됐는가
□ SEO JSON-LD가 있는가
□ 마스트헤드가 있는가
□ 수치 대시보드가 있는가
□ 히어로 이미지가 Unsplash URL인가
□ SVG를 쓰지 않았는가
□ 멋쟁이의 시각 박스가 있는가
□ 출처 표기 푸터가 있는가
□ 종목 픽에 팩트 근거가 있는가
□ 종목 픽에 리스크도 언급했는가

위 12개 중 하나라도 없으면 재작성한다.
"""

# ────────────────────────────────
# Heading 태그의 line-height 자동 보정 (겹침 방지)
# ────────────────────────────────
def fix_heading_line_height(html_content: str) -> str:
    import re
    def repl(match):
        tag = match.group(1)   # e.g., 'h1'
        attrs = match.group(2) # e.g., 'style="..."'
        
        style_match = re.search(r'style="([^"]*)"', attrs)
        if style_match:
            style_content = style_match.group(1).strip()
            if 'line-height' not in style_content:
                if style_content and not style_content.endswith(';'):
                    style_content += ';'
                style_content += ' line-height: 1.4;'
            new_style = f'style="{style_content}"'
            new_attrs = re.sub(r'style="[^"]*"', new_style, attrs)
            return f'<{tag} {new_attrs}>'
        else:
            return f'<{tag} style="line-height: 1.4;" {attrs}>'

    pattern = r'<(h[1-6])\b([^>]*)>'
    return re.sub(pattern, repl, html_content, flags=re.IGNORECASE)

# ────────────────────────────────
# 마크다운 ** 및 이모지/특수 기호 제거
# ────────────────────────────────
def clean_html_content(html_content: str) -> str:
    import re
    # 1. 마크다운 별표(**) 제거
    html_content = html_content.replace("**", "")
    
    # 2. 이모지 및 특수 데코용 기호 제거 (정규식 활용)
    emoji_pattern = re.compile(
        '['
        '\U0001F600-\U0001F64F'  # emoticons
        '\U0001F300-\U0001F5FF'  # symbols & pictographs
        '\U0001F680-\U0001F6FF'  # transport & map symbols
        '\U0001F1E0-\U0001F1FF'  # flags
        '\U0001F900-\U0001F9FF'  # supplemental symbols
        '\u2600-\u26FF'          # misc symbols
        '\u2700-\u27BF'          # dingbats
        '\ufe0f'                 # variation selector
        ']+', flags=re.UNICODE
    )
    html_content = emoji_pattern.sub('', html_content)
    
    # 혹시 남을 수 있는 대표적인 데코용 특수문자 개별 소거
    for char in ["📊", "🤖", "⚠️", "✅", "✔", "📈", "📉", "🔥", "💡", "📢", "🔍", "⚡", "⭐", "☑", "✨"]:
        html_content = html_content.replace(char, "")

    # 3. 절대 금지 표현 방어적 교체 (이중 레이어 방어막)
    forbidden_replacements = {
        "급등 예상": "상승 흐름 전망",
        "지금이 매수 타이밍": "관심 구간 진입 판단",
        "오전 9시 진입하라": "개장 후 흐름 모니터링",
        "방아쇠를 당겨라": "리스크를 검토하라",
        "놓치면 후회한다": "유의 깊게 관찰해야 한다",
        "이 종목을 주목하라": "이 종목의 공시 분석",
        "수익을 챙겨라": "수익 관리에 유의하라",
        "반드시 오른다": "상승 가능성이 높다",
        "승리할 것이다": "안정적인 흐름이 기대된다",
        "이미 포지션을 구축했다": "포지션 전략을 검토했다",
        "압도적 수익 추구": "포트폴리오 수익 극대화",
        "비대칭 포지셔닝": "비대칭 포지션 검토",
        "멋쟁이만 아는": "멋쟁이 분석의",
        "독점 분석": "심층 분석",
        "지금 바로 확인": "참조 가능",
    }
    for old, new in forbidden_replacements.items():
        html_content = html_content.replace(old, new)
        
    return html_content

# ────────────────────────────────
# 투자 고지(Disclaimer) 보장 및 닫는 태그 보정
# ────────────────────────────────
# ────────────────────────────────
# HTML 클래스를 인라인 스타일로 변환 (토큰 절약 및 호환성 보장)
# ────────────────────────────────
def inline_css_styles(html_content: str) -> str:
    styles_map = {
        "mi-container": "max-width: 720px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; color: #1a1a1a; line-height: 1.9; padding: 0 4px;",
        "mi-section-header": "font-size: 10px; letter-spacing: 0.2em; color: #888; border-bottom: 1.5px solid #0a0a0a; padding-bottom: 6px; margin: 30px 0 14px; font-weight: bold;",
        "mi-paragraph": "font-size: 14px; color: #2c2c2c; line-height: 1.95; margin: 0 0 14px; text-align: justify; word-break: keep-all;",
        
        "mi-card-positive": "border-left: 3px solid #4ade80; background: #f9f8f5; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-positive-title": "font-size: 13px; font-weight: 700; color: #1a7a4a; margin: 0 0 4px;",
        
        "mi-card-negative": "border-left: 3px solid #ef4444; background: #fff5f5; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-negative-title": "font-size: 13px; font-weight: 700; color: #c0392b; margin: 0 0 4px;",
        
        "mi-card-neutral": "border-left: 3px solid #888; background: #f9f8f5; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-neutral-title": "font-size: 13px; font-weight: 700; color: #555; margin: 0 0 4px;",
        
        "mi-card-blue": "border-left: 3px solid #1a3a6b; background: #f9f8f5; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-blue-title": "font-size: 13px; font-weight: 700; color: #1a3a6b; margin: 0 0 4px;",
        
        "mi-card-content": "font-size: 13px; color: #2c2c2c; line-height: 1.85; margin: 0;",
        
        "mi-dark-box": "background: #0a0a0a; padding: 16px 18px; margin: 16px 0 4px;",
        "mi-dark-box-title": "font-size: 9px; letter-spacing: 0.18em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-dark-box-content": "color: #e2e2e2; font-size: 14px; line-height: 1.9; margin: 0;",
        
        "mi-group-container": "border: 1px solid #e0ddd6; margin: 0 0 10px; border-radius: 4px; overflow: hidden;",
        "mi-group-header-a": "background: #1a3a6b; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-b": "background: #555; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-c": "background: #c0392b; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-title": "font-size: 11px; font-weight: 700; color: #fff; margin: 0;",
        "mi-group-header-stars": "font-size: 11px; color: #f0c040; margin: 0;",
        "mi-group-content": "padding: 12px 16px;",
        
        "mi-headline-container": "padding: 0 0 18px; border-bottom: 2px solid #0a0a0a;",
        "mi-headline-meta": "font-size: 11px; letter-spacing: 0.15em; color: #c0392b; margin: 0 0 8px; font-weight: bold;",
        "mi-headline-title": "font-family: Georgia, serif; font-size: 26px; font-weight: 700; line-height: 1.15; margin: 0 0 12px; letter-spacing: -0.02em;",
        "mi-headline-lead": "font-size: 14px; color: #444; line-height: 1.85; margin: 0; border-left: 4px solid #c0392b; padding-left: 14px;",
        
        "mi-disclaimer-table": "border-collapse: collapse; border: 2px solid #c0392b; margin: 24px 0 0; width: 100%;",
        "mi-disclaimer-header": "background: #c0392b; padding: 10px 16px;",
        "mi-disclaimer-content": "background: #fff8f7; padding: 12px 16px; text-align: left;"
    }
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 일반 클래스 인라인 처리
    for class_name, style_str in styles_map.items():
        elements = soup.find_all(class_=class_name)
        for el in elements:
            existing_style = el.get("style", "")
            if existing_style:
                el["style"] = style_str + " " + existing_style
            else:
                el["style"] = style_str
                
    # 2. 멋쟁이 픽 그룹 내용물의 p 태그들 인라인 처리
    group_contents = soup.find_all(class_="mi-group-content")
    for gc in group_contents:
        p_tags = gc.find_all("p")
        for i, p in enumerate(p_tags):
            p_style = "font-size: 13.5px; color: #2c2c2c; line-height: 1.85;"
            if i < len(p_tags) - 1:
                p_style += " margin: 0 0 8px;"
            else:
                p_style += " margin: 0;"
            
            existing = p.get("style", "")
            if existing:
                p["style"] = p_style + " " + existing
            else:
                p["style"] = p_style

    # 3. 투자 고지 안쪽 내용 처리
    disclaimer_content_td = soup.find(class_="mi-disclaimer-content")
    if disclaimer_content_td:
        p_tags = disclaimer_content_td.find_all("p")
        for i, p in enumerate(p_tags):
            p_style = "font-size: 12.5px; color: #5a1a1a; line-height: 1.8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;"
            if i < len(p_tags) - 1:
                p_style += " margin: 0 0 8px;"
            else:
                p_style += " margin: 0;"
            
            existing = p.get("style", "")
            if existing:
                p["style"] = p_style + " " + existing
            else:
                p["style"] = p_style
                
    disclaimer_header_td = soup.find(class_="mi-disclaimer-header")
    if disclaimer_header_td:
        p_tag = disclaimer_header_td.find("p")
        if p_tag:
            p_style = "font-size: 11px; font-weight: 700; color: #fff; margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;"
            existing = p_tag.get("style", "")
            if existing:
                p_tag["style"] = p_style + " " + existing
            else:
                p_tag["style"] = p_style

    return str(soup)

# ────────────────────────────────
# 투자 고지(Disclaimer) 보장 및 닫는 태그 보정
# ────────────────────────────────
def ensure_disclaimer_and_closed_tags(html_content: str) -> str:
    # 0. 마크다운 기호 및 이모지 자동 정화
    html_content = clean_html_content(html_content)

    # 1. 잘려나간 마지막 불완전한 태그 제거 (예: <p style="font-size: 1.1em; 로 끝나는 경우)
    last_open_angle = html_content.rfind("<")
    last_close_angle = html_content.rfind(">")
    if last_open_angle > last_close_angle:
        print(f"⚠️ 경고: 불완전한 태그 '{html_content[last_open_angle:]}'를 잘라내어 문장을 정리합니다.")
        html_content = html_content[:last_open_angle]

    # 2. 열려있는 div 및 table 태그 분석 후 '먼저' 닫아주기 (중첩 방지)
    import re
    # 시작 태그와 종료 태그 매칭
    tags = re.findall(r'<(div|table)\b[^>]*>|</(div|table)>', html_content, re.IGNORECASE)
    open_tags = []
    for tag in tags:
        if tag[0]:  # 시작 태그
            open_tags.append(tag[0].lower())
        elif tag[1]:  # 종료 태그
            t_close = tag[1].lower()
            if open_tags and open_tags[-1] == t_close:
                open_tags.pop()
            elif t_close in open_tags:
                open_tags.remove(t_close)
                
    if open_tags:
        closing_str = ""
        for t in reversed(open_tags):
            closing_str += f"</{t}>"
        print(f"⚠️ 경고: 잘린 HTML 복구를 위해 열린 태그를 먼저 닫습니다: {open_tags} -> {closing_str}")
        html_content += closing_str

    # 3. 투자 고지 문구 존재 여부 확인 및 보정
    has_disclaimer = any(word in html_content for word in ["Disclaimer", "투자 고지", "투자고지", "투자 주의", "투자주의", "투자 판단의 참고 자료"])
    if not has_disclaimer:
        print("⚠️ 경고: AI 생성 결과에 투자 고지(Disclaimer)가 누락되거나 잘렸습니다. 자동으로 보정합니다.")
        disclaimer_html = """
    <!-- 자동 보정된 투자 고지 영역 -->
    <table class="mi-disclaimer-table">
        <tr>
            <td class="mi-disclaimer-header">
                <p>투자 위험 고지</p>
            </td>
        </tr>
        <tr>
            <td class="mi-disclaimer-content">
                <p><strong>투자 판단의 참고 자료:</strong> 본 리포트에서 제공하는 모든 정보(수치, 전망, 분석 결과 등)는 투자 판단을 돕기 위한 참고용 자료일 뿐이며, 어떠한 경우에도 특정 금융 상품이나 주식 종목의 매수·매도 권유 또는 투자 추천으로 해석될 수 없습니다. 본 정보는 공시 및 신뢰할 만한 취재원을 바탕으로 작성되었으나 그 완전성이나 정확성을 전적으로 보장할 수 없으므로 실제 투자 실행 전 반드시 추가적인 검증이 필요합니다.</p>
                <p><strong>최종 책임의 귀속:</strong> 모든 투자의 최종 의사결정과 그 결과에 대한 책임은 전적으로 투자자 본인에게 귀속되며, 본 리포트는 어떠한 법적 책임도 지지 않습니다.</p>
                <p><strong>전문가 상담 권고:</strong> 투자를 실행하기 전에는 반드시 충분한 시장 확인과 공인된 전문가와의 상담을 거치시기 바랍니다.</p>
            </td>
        </tr>
    </table>
"""
        html_content += disclaimer_html
        
    # 4. 클래스 기반 태그들을 인라인 스타일로 전격 변환
    html_content = inline_css_styles(html_content)
        
    return html_content

# ────────────────────────────────
# Gemini API 호출
# ────────────────────────────────
def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY 없음 → Anthropic으로 대체")
        return call_anthropic(prompt)
    
    # 1. Gemini 2.5 Flash 시도
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.3,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }
    
    try:
        print("🤖 Gemini 2.5 Flash 호출 중...")
        res = requests.post(url, json=body, timeout=120)
        data = res.json()
        if "error" in data:
            raise RuntimeError(f"Gemini 2.5 API 에러: {data['error'].get('message')}")
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"⚠️ Gemini 2.5 Flash 호출 실패 ({e}) → gemini-flash-latest (1.5 Flash)로 대체 시도...")
        try:
            # 2. Gemini 1.5 Flash (gemini-flash-latest) 시도
            url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
            body_fallback = {
                "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 8192,
                    "temperature": 0.3,
                    "thinkingConfig": {
                        "thinkingBudget": 0
                    }
                }
            }
            res = requests.post(url_fallback, json=body_fallback, timeout=120)
            data = res.json()
            if "error" in data:
                raise RuntimeError(f"Gemini 1.5 API 에러: {data['error'].get('message')}")
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as fallback_err:
            print(f"⚠️ Gemini 1.5 Flash 호출 실패 ({fallback_err}) → Anthropic으로 대체 시도...")
            try:
                # 3. Anthropic (Claude 3.5 Sonnet) 시도
                return call_anthropic(prompt)
            except Exception as ae:
                raise RuntimeError(f"모든 AI API 호출에 실패했습니다. (Gemini 2.5: {e}, Gemini 1.5: {fallback_err}, Anthropic: {ae})")
                
    # HTML 블록만 추출
    if "```html" in text:
        text = text.split("```html")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    processed_text = fix_heading_line_height(text)
    return ensure_disclaimer_and_closed_tags(processed_text)

# ────────────────────────────────
# Anthropic API 호출 (백업)
# ────────────────────────────────
def call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text
    if "```html" in text:
        text = text.split("```html")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    processed_text = fix_heading_line_height(text)
    return ensure_disclaimer_and_closed_tags(processed_text)

# ────────────────────────────────
# 일일 리포트 생성
# ────────────────────────────────
def generate_daily_report(market_data: dict, news_data: dict) -> str:
    import datetime
    today = datetime.datetime.now()
    
    # 실행 시점이 주말(토/일)인지 평일인지 판별하여 개장일 정보 동적 설정
    current_weekday = today.weekday()
    if current_weekday == 5:  # 토요일
        target_date = today + datetime.timedelta(days=2)
        trading_day_word = "다음 거래일(월요일)"
    elif current_weekday == 6:  # 일요일
        target_date = today + datetime.timedelta(days=1)
        trading_day_word = "다음 거래일(월요일)"
    else:  # 평일
        target_date = today
        trading_day_word = "오늘"
        
    target_date_str = target_date.strftime("%Y년 %m월 %d일")
    target_weekday = ["월","화","수","목","금","토","일"][target_date.weekday()]

    prompt = f"""
리포트 작성 기준일: {today.strftime("%Y년 %m월 %d일")} (현재 실행 시점)
목표 개장일(국장 기준): {target_date_str} ({target_weekday}요일)
개장일 지칭 표현: {trading_day_word}
브리핑 종류: 오전 브리핑

=== 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 오전 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 출력 토큰 제한으로 인해 글이 잘리는 것을 완전히 방지해야 합니다. 각 본문 섹션(I~V)의 본문 단락은 구구절절한 설명을 모두 제거하고, 1~2개 문장으로 사실만 요약하여 극도로 간결하게 작성하십시오. 
- [중요 - 시나리오 및 멋쟁이 픽 단축]: 결론의 낙관/중립/비관 3대 시나리오 역시 각 1줄 내외로 핵심만 적고, 멋쟁이 픽 종목 역시 2줄 내외로 팩트와 리스크만 짧게 요약하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 3,000자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 문구를 포함한 세련된 구조)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 오늘 핵심 키워드, 오른쪽: 가장 중요한 수치 골드 #f0c040)
  4. 수치 대시보드 (table, 검정 배경, 4칸 x 2행 = 8개 핵심 지표 수치 표시)
  5. 출처 표기 (font-size 11px, 회색, 대시보드 수치의 출처 한 줄 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 역설형/숫자형/궁금증형 패턴 활용)
  8. 본문 섹션 (로마숫자 I·II·III·IV·V)
     - I. 글로벌 매크로 — 달러·금리·유가 삼각 분석
     - II. 한국 시장 포지션 — 글로벌 자금 흐름에서 한국의 위치
     - III. 수급 분석 — 외국인·기관·개인 의미 해석 (실제 수치 기반)
     - IV. 오늘 주목 이벤트 — 공시·발표·지표 (DART 공시 및 뉴스 정보 연결)
     - V. 멋쟁이 픽 — 팩트 기반 관심 종목 (A그룹·B그룹·C그룹 분류, 각 종목별 구체적 팩트 근거 및 하락 리스크 동시 서술, 별점 ★★★★★ ~ ★★★☆☆ 표시)
  9. 결론: 멋쟁이의 시각 박스 (배경 #0a0a0a, 낙관/중립/비관 3대 대응 시나리오 반드시 포함)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 검색 포털(네이버, 구글 등)에서 트래픽을 대량으로 유입시킬 수 있는 핵심 검색 키워드를 조합하여 자극적으로 작성하십시오.
- 코스피 전망, 삼성전자, 마이크론, FOMC 등 그날의 가장 중요한 매크로/기업 검색 키워드를 포함하십시오.

div-only HTML 전체 출력.
"""
    print("🤖 AI 리포트 생성 중...")
    result = call_gemini(prompt)
    print("✅ 리포트 생성 완료")
    return result

# ────────────────────────────────
# 오후 마감 리포트 생성 (신규)
# ────────────────────────────────
def generate_afternoon_report(market_data: dict, news_data: dict) -> str:
    import datetime
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    prompt = f"""
리포트 작성 기준일: {date_str} ({weekday}요일)
브리핑 종류: 오후 마감 브리핑

=== 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 오후 마감 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 출력 토큰 제한으로 인해 글이 잘리는 것을 완전히 방지해야 합니다. 각 본문 섹션(I~V)의 본문 단락은 구구절절한 설명을 모두 제거하고, 1~2개 문장으로 사실만 요약하여 극도로 간결하게 작성하십시오.
- [중요 - 시나리오 및 결론 단축]: 결론의 내일을 위한 전략 3가지 시나리오 역시 각 1줄 내외로 핵심만 짧게 요약하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 3,000자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 문구를 포함한 세련된 구조)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 오늘 핵심 키워드, 오른쪽: 가장 중요한 수치 골드 #f0c040)
  4. 수치 대시보드 (table, 검정 배경, 4칸 x 2행 = 8개 핵심 지표 수치 표시)
  5. 출처 표기 (font-size 11px, 회색, 대시보드 수치의 출처 한 줄 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 역설형/숫자형/궁금증형 패턴 활용)
  8. 본문 섹션 (로마숫자 I·II·III·IV·V)
     - I. 오늘 마감 결과 해석 — 숫자의 의미 (장 마감 지수 및 거래대금 등)
     - II. 수급 분석 — 오늘 외국인·기관·개인이 한 행동 (순매수/순매도 규모 분석)
     - III. 오늘 상한가·급등 종목 — 팩트 기반 이유 (원인 및 공시 매칭)
     - IV. 내일을 위한 전략 — 3가지 시나리오 (다음 거래일 대응법)
     - V. 오늘 주요 공시 — 가장 중요한 것 1개 (DART 공시의 구체적 설명)
  9. 결론: 이번 주 흐름에서 오늘의 위치 (멋쟁이의 시각 박스 포함)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 검색 포털(네이버, 구글 등)에서 트래픽을 대량으로 유입시킬 수 있는 핵심 검색 키워드를 조합하여 자극적으로 작성하십시오.
- 코스피 마감, 환율, 상승 종목, 공시 등 그날의 가장 중요한 매크로/기업 검색 키워드를 포함하십시오.

div-only HTML 전체 출력.
"""
    print("🤖 AI 오후 마감 리포트 생성 중...")
    result = call_gemini(prompt)
    print("✅ 오후 마감 리포트 생성 완료")
    return result

# ────────────────────────────────
# 주간 결산 리포트
# ────────────────────────────────
def generate_weekly_report(market_data: dict, news_data: dict) -> str:
    today = datetime.datetime.now()
    
    # 다음 주 월~금 날짜 계산 (기존의 날짜/요일 오류 방지)
    current_weekday = today.weekday()
    if current_weekday == 6:  # 일요일
        days_to_monday = 1
    elif current_weekday == 5:  # 토요일
        days_to_monday = 2
    else:  # 평일
        days_to_monday = 7 - current_weekday
        
    next_monday = today + datetime.timedelta(days=days_to_monday)
    
    weekday_names = ["월", "화", "수", "목", "금"]
    next_week_info = []
    for i in range(5):
        day = next_monday + datetime.timedelta(days=i)
        next_week_info.append(f"- {weekday_names[i]}요일: {day.strftime('%m월 %d일')}")
        
    next_week_dates_str = "\n".join(next_week_info)
    next_week_range_str = f"{next_monday.strftime('%Y.%m.%d')} - {(next_monday + datetime.timedelta(days=4)).strftime('%m.%d')}"

    prompt = f"""
주간 결산: {today.strftime("%Y년 %m월 %d일")} (토요일/일요일 결산용)
브리핑 종류: 주간 결산
다음 주 날짜 정보 (한국 시간 기준):
기간: {next_week_range_str}
{next_week_dates_str}

=== 주간 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 주간 뉴스 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 주간 결산 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 출력 토큰 제한으로 인해 글이 잘리는 것을 완전히 방지해야 합니다. 각 본문 섹션(I~V)의 본문 단락은 구구절절한 설명을 모두 제거하고, 1~2개 문장으로 사실만 요약하여 극도로 간결하게 작성하십시오.
- [중요 - 시나리오 및 멋쟁이 픽 단축]: 결론의 다음 주 대응 전술 및 3개 전략 시나리오 역시 각 1줄 내외로 핵심만 적고, 멋쟁이 픽 종목 역시 2줄 내외로 팩트와 리스크만 짧게 요약하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 3,000자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 문구를 포함한 세련된 구조)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 이번 주 핵심 키워드, 오른쪽: 가장 중요한 수치 골드 #f0c040)
  4. 수치 대시보드 (table, 검정 배경, 4칸 x 2행 = 8개 핵심 지표 수치 표시)
  5. 출처 표기 (font-size 11px, 회색, 대시보드 수치의 출처 한 줄 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 역설형/숫자형/궁금증형 패턴 활용)
  8. 본문 섹션 (로마숫자 I·II·III·IV·V)
     - I. 이번 주 핵심 사건 3가지 — 구조적 의미 (이벤트 분석)
     - II. 글로벌 자금 흐름 주간 진단 (유동성 및 매크로 환경 변화)
     - III. 코스피·코스닥 주간 수익률 해석 (지수 수익률의 실제 수치와 의미)
     - IV. 다음 주 핵심 이벤트 캘린더 (반드시 날짜와 요일 정확히 매칭)
     - V. 다음 주 멋쟁이 픽 (팩트 기반 관심 종목, 종목별 하락 리스크 필수 기재)
  9. 결론: 멋쟁이의 시각 박스 (배경 #0a0a0a, 다음 주 대응 전술과 3개 전략 시나리오 요약)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 주간 결산 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 주간 결산에 걸맞게 한 주간의 흐름과 다음 주 전망 키워드를 강력하게 매칭하여 클릭을 유도하도록 작성하십시오.
- '코스피 주간 결산', '다음 주 주가 전망', '반도체/금리 등 핵심 테마명', '엔비디아/삼성전자 등 주요 기업명' 검색 키워드를 포함하십시오.

div-only HTML 전체 출력.
"""
    return call_gemini(prompt)

if __name__ == "__main__":
    print("Gemini API Key:", "있음" if GEMINI_API_KEY else "없음 (Anthropic 사용)")
    print("Anthropic API Key:", "있음" if ANTHROPIC_API_KEY else "없음")
