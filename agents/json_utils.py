"""
agents/json_utils.py — 강건한 JSON 추출 유틸리티
Claude가 반환하는 텍스트에서 JSON을 안전하게 파싱합니다.
- 코드블록(```json ... ```) 내 JSON 추출
- 불완전한 JSON 교정 시도
- 최후 수단으로 빈 dict 반환 (파이프라인 중단 방지)
"""
import json
import re


def extract_json(text: str) -> dict:
    """
    Claude 응답 텍스트에서 JSON을 최대한 안전하게 추출합니다.
    
    시도 순서:
    1. ```json ... ``` 코드블록 내 JSON
    2. 첫 { ~ 마지막 } 사이 파싱
    3. 줄바꿈·탭 정규화 후 재시도
    4. json5 스타일 완화 파싱 (trailing comma 등)
    5. 실패 시 {"error": "파싱 실패"} 반환
    """
    if not text:
        return {"error": "빈 응답"}

    text = text.strip()

    # 1. 코드블록 내 JSON 추출 시도
    code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_match:
        candidate = code_match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 2. 첫 { ~ 마지막 } 추출
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"error": "JSON 객체 없음", "raw": text[:200]}

    candidate = text[start:end + 1]

    # 3. 직접 파싱 시도
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 4. 줄바꿈·제어문자 정규화 후 재시도
    cleaned = _sanitize_json_string(candidate)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 5. 점진적 잘라내기 (JSON 끝이 잘린 경우)
    truncated = _try_truncate_to_valid(cleaned)
    if truncated:
        try:
            return json.loads(truncated)
        except json.JSONDecodeError:
            pass

    # 6. 최후 수단: 오류 반환
    return {"error": "JSON 파싱 실패", "raw_preview": candidate[:300]}


def _sanitize_json_string(text: str) -> str:
    """JSON 문자열 내부의 비정상 문자를 정규화합니다."""
    # 문자열 값 내부의 줄바꿈을 \\n으로 치환
    # 큰따옴표로 묶인 값 안의 줄바꿈만 처리 (키/구조는 건드리지 않음)
    def fix_string_value(m):
        inner = m.group(1)
        # 문자열 내부 줄바꿈 → \n 이스케이프
        inner = inner.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        # 이미 이스케이프된 것을 이중 이스케이프하지 않도록
        inner = inner.replace('\\\\n', '\\n').replace('\\\\r', '\\r').replace('\\\\t', '\\t')
        return f'"{inner}"'

    # JSON 문자열 값 내부 처리 (간단한 패턴)
    text = re.sub(r'"((?:[^"\\]|\\.)*)"', fix_string_value, text)
    
    # trailing comma 제거: }, 또는 ] 앞의 ,
    text = re.sub(r',\s*([}\]])', r'\1', text)
    
    return text


def _try_truncate_to_valid(text: str) -> str | None:
    """JSON이 중간에 잘린 경우 마지막 완전한 키-값 쌍까지 자르고 닫습니다."""
    # 열린 괄호 수를 세어 균형 맞추기
    depth = 0
    last_valid_end = 0
    in_string = False
    escape = False
    
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                last_valid_end = i + 1
                break
    
    if last_valid_end > 0:
        return text[:last_valid_end]
    return None
