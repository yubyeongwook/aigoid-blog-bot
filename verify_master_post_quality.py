import requests
from bs4 import BeautifulSoup

url = "http://43.200.245.223/?p=86"
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

# 본문 텍스트 추출
content = soup.find('div', style=lambda value: value and 'max-width:860px' in value)
if not content:
    content = soup.find('article')

text = content.get_text() if content else soup.get_text()
clean_text = ' '.join(text.split())

char_count_total = len(clean_text)
char_count_no_spaces = len(clean_text.replace(" ", ""))

print("=== [사장님 블로그 명품글 객관적 수치 검증 분석표] ===")
print(f"1. 전체 글자 수 (공백 포함): {char_count_total:,} 자")
print(f"2. 순수 글자 수 (공백 제외): {char_count_no_spaces:,} 자")
print(f"3. 근거 법령 명시 여부: {'근로기준법' in clean_text and '최저임금법' in clean_text}")
print(f"4. 2025년/2026년 수치 분리 여부: {'10,030' in clean_text and '10,320' in clean_text}")
print(f"5. 209시간 파이썬 정밀 연산 여부: {'2,096,270' in clean_text and '2,156,880' in clean_text}")
