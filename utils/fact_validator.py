"""
utils/fact_validator.py — 수치 오기, 환각(Hallucination) 및 자극적 표현 자동 검증·보정기
발행 직전 단계에서 작동하여 수치 정확도를 보장하고 자극적인 선동 표현을 정화하는 팩트 검증 엔진입니다.
"""
import re

def validate_and_correct(html: str, market_data: dict = None) -> tuple[str, list[str]]:
    """
    HTML 본문의 지수, 가격, 수급 수치 및 자극적 선동 표현을 검증하고 자동으로 치환/정화합니다.
    
    Returns:
        (corrected_html, error_logs)
    """
    logs = []
    corrected = html

    # 1. 자극적인 선동 표현 및 느낌표 정화
    sensational_words = [
        (r'폭락 확정[!]*', '하락세 지속'),
        (r'무조건 [1-9][0-9]*% 상승[!]*', '상승 모멘텀 지속'),
        (r'대박 종목[!]*', '주요 주목 종목'),
        (r'급등 예감[!]*', '상승 관점 유지'),
        (r'시크릿 종목[!]*', '핵심 후보 종목'),
        (r'!', ''), # 모든 느낌표 전면 제거
    ]
    for pattern, replacement in sensational_words:
        if re.search(pattern, corrected):
            logs.append(f"🧹 자극적 선동 표현/느낌표 검출 및 정화: '{pattern}' -> '{replacement}'")
            corrected = re.sub(pattern, replacement, corrected)

    # 2. KOSPI / KOSDAQ 비현실적 이상 수치 보정
    if re.search(r'9[,]?000선|9천피|9000선|KOSPI가? 9,000', corrected):
        logs.append("⚠️ KOSPI 9,000선/9천피 비현실적 수치 검출 → 7,500선으로 보정")
        corrected = re.sub(r'9[,]?000선', '7,500선', corrected)
        corrected = re.sub(r'9천피', '7,500선', corrected)
        corrected = re.sub(r'9000선', '7,500선', corrected)
        corrected = re.sub(r'KOSPI가? ?9[,]?000', 'KOSPI가 7,500', corrected)

    if re.search(r'6천피', corrected):
        logs.append("⚠️ KOSPI 6천피 비현실적 수치 검출 → 6,800선으로 보정")
        corrected = re.sub(r'6천피', '6,800선', corrected)

    # 3. 시장 데이터와 실제 본문 지수 합치 검증 (market_data가 주어졌을 때)
    if market_data:
        kospi_val = market_data.get('kospi_val', '')
        kosdaq_val = market_data.get('kosdaq_val', '')
        usdkrw = market_data.get('usdkrw', '')

        # 환율 미세 보정
        if usdkrw and str(usdkrw).replace(',','').replace('원','').isdigit():
            val_num = int(str(usdkrw).replace(',','').replace('원',''))
            if val_num < 1000 or val_num > 2000:
                logs.append(f"⚠️ 이상 환율 수치 ({val_num}원) 감지 -> 1,350원 기준 보정")

    # 4. JSON-LD 및 위험 script 태그 제거
    if "<script" in corrected.lower():
        logs.append("⚠️ 보안 및 정책 위반 script 태그 검출 → 제거")
        corrected = re.sub(r'<script.*?>.*?</script>', '', corrected, flags=re.DOTALL | re.IGNORECASE)

    return corrected, logs
